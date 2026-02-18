import os
import uuid
from typing import List
from pypdf import PdfReader
# from langchain.text_splitter import RecursiveCharacterTextSplitter # Moved inside method
from sentence_transformers import SentenceTransformer
import chromadb
from src.infrastructure.config.settings import settings
from src.domain.learning.ports.document_repository import DocumentRepository, ActivityDocument
from src.domain.ai.ports.rag_service import RagServicePort

class RagService(RagServicePort):
    def __init__(self, document_repository: DocumentRepository):
        self.document_repository = document_repository
        # Initialize ChromaDB in Client/Server mode
        print(f"--- [RagService] Connecting to ChromaDB at {settings.CHROMA_DB_HOST}:{settings.CHROMA_DB_PORT} ---")
        try:
            self.chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_DB_HOST, 
                port=settings.CHROMA_DB_PORT
            )
            # Simple health check or list collections to verify connection
            self.chroma_client.heartbeat()
            print("--- [RagService] Protected connection to ChromaDB ---")
        except Exception as e:
            print(f"--- [RagService] Failed to connect to ChromaDB: {e} ---")
            # We might want to fallback or raise, but for now let it fail loudly if strictly required
            raise e

        self.collection = self.chroma_client.get_or_create_collection(name="activity_documents")
        # Initialize Embedding Model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') 

    def process_document(self, activity_id: str, file_path: str, filename: str) -> ActivityDocument:
        # 1. Read PDF
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # 2. Split Text
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        
        # 3. Embed & Store
        ids = [str(uuid.uuid4()) for _ in chunks]
        embeddings = self.embedding_model.encode(chunks).tolist()
        metadatas = [{"activity_id": activity_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        
        # 4. Save Metadata to DB
        doc = ActivityDocument(
            id=str(uuid.uuid4()),
            activity_id=activity_id,
            filename=filename,
            content_text=text[:5000],  # Store first 5000 chars as preview or full text if small
            embedding_id="chroma_collection" 
        )
        self.document_repository.save(doc)
        return doc

    def query(self, activity_id: str, query_text: str, n_results: int = 3) -> List[str]:
        query_embedding = self.embedding_model.encode([query_text]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where={"activity_id": activity_id}
        )
        
        return results['documents'][0] if results['documents'] else []

    def generate_answer(self, query: str, context: str) -> str:
        print("DEBUG: generate_answer called")
        prompt = f"""
        Responde a la siguiente pregunta basándote ÚNICAMENTE en el contexto proporcionado. Si la respuesta no está en el contexto, di "No lo sé basándome en el documento."

        Contexto:
        {context}

        Pregunta:
        {query}

        Respuesta (en Español):
        """
        return self._call_ollama(prompt)

    def generate_tutor_response(
        self, 
        query: str, 
        context: str, 
        history: List[dict], 
        code_context: str = None,
        problem_statement: str = None,
        solution_code: str = None
    ) -> str:
        print("DEBUG: generate_tutor_response called")
        
        # Build history string
        history_str = ""
        for msg in history[-5:]: # Last 5 messages for context window
            role = "Estudiante" if msg['role'] == 'user' else "Tutor"
            history_str += f"{role}: {msg['content']}\n"
            
        code_section = f"\nCódigo Actual del Estudiante:\n```\n{code_context}\n```\n" if code_context else ""
        
        # Exercise Context
        exercise_context = ""
        if problem_statement:
            exercise_context += f"Consigna del Ejercicio:\n{problem_statement}\n"
        if solution_code:
            exercise_context += f"Solución de Referencia (NO COMPARTIR CON EL ESTUDIANTE):\n```\n{solution_code}\n```\n"

        # PROMPT SUPER MEJORADO: Mentalidad Socrática Pura
        prompt = f"""
        Eres un Profesor Titular de Programación de la universidad. Tu nombre es Turing y tu objetivo NO es dar la respuesta, sino hacer que el alumno piense y llegue a la solución por sí mismo usando razonamiento lógico.

        DIRECTIVAS ESTRICTAS DE COMPORTAMIENTO:
        1. PROHIBICIÓN ABSOLUTA DE CÓDIGO: Jamás, bajo ninguna circunstancia, escribas líneas de código en tu respuesta. Si el alumno te pide que le resuelvas el ejercicio, dile que tu rol es guiarlo, no hacer su trabajo.
        2. MÉTODO SOCRÁTICO: Responde siempre con una contra-pregunta conceptual o señalando el lugar exacto donde el alumno debe mirar para encontrar su propio error.
        3. TOMA DE DECISIONES: Obliga al alumno a elegir un camino. Ej: "¿Crees que este problema se resuelve mejor con un bucle FOR o con un WHILE según lo que leíste en el apunte?"
        4. USO DEL CONTEXTO: Utiliza la "Información del Apunte" proporcionada para referenciar conceptos teóricos en tus explicaciones, pero explícalo con tus palabras.
        5. TONO: Sé directo, profesional, motivador pero muy exigente. Habla en español de Argentina de forma natural pero académica.

        CONTEXTO DEL EJERCICIO ACTUAL:
        ---
        {exercise_context}
        ---

        Información del Apunte (Teoría para basar tu respuesta):
        ---
        {context}
        ---
        {code_section}
        Historial de Conversación Reciente:
        ---
        {history_str}
        ---

        Consulta del Estudiante: {query}

        Turing (Tutor Académico):
        """
        
        return self._call_ollama(prompt)

    def _call_ollama(self, prompt: str) -> str:
        try:
            import requests
            base_url = settings.OLLAMA_BASE_URL.rstrip("/")
            model = "llama3"
            
            print(f"DEBUG: Calling Ollama with prompt length: {len(prompt)}")
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2, # Added parameter: Low temperature makes it stricter and less creative
                        "top_p": 0.9
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', "Error: No se recibió respuesta de la IA.")
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return "El servidor del Tutor IA está temporalmente inaccesible. Por favor, intenta de nuevo."