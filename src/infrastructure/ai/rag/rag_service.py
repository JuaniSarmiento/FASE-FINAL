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
            print("--- [RagService] Successfully connected to ChromaDB ---")
        except Exception as e:
            error_msg = f"Failed to connect to ChromaDB at {settings.CHROMA_DB_HOST}:{settings.CHROMA_DB_PORT}"
            print(f"--- [RagService] ERROR: {error_msg} ---")
            print(f"--- [RagService] Details: {str(e)} ---")
            print(f"--- [RagService] HINT: Make sure ChromaDB is running. For Docker: docker-compose up chroma ---")
            raise ConnectionError(error_msg) from e

        self.collection = self.chroma_client.get_or_create_collection(name="activity_documents")
        # Initialize Embedding Model
        print("--- [RagService] Loading embedding model 'all-MiniLM-L6-v2'... ---")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("--- [RagService] Embedding model loaded successfully ---") 

    def process_document(self, activity_id: str, file_path: str, filename: str) -> ActivityDocument:
        print(f"--- [RagService] Processing document: {filename} for activity {activity_id} ---")
        
        # 1. Read PDF
        try:
            print(f"--- [RagService] Reading PDF from {file_path} ---")
            reader = PdfReader(file_path)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += page_text
                print(f"--- [RagService] Extracted {len(page_text)} chars from page {page_num + 1} ---")
            
            print(f"--- [RagService] Total extracted text: {len(text)} characters ---")
            
            if not text.strip():
                raise ValueError("PDF file appears to be empty or contains no extractable text")
                
        except Exception as e:
            error_msg = f"Failed to read PDF file: {str(e)}"
            print(f"--- [RagService] ERROR: {error_msg} ---")
            raise ValueError(error_msg) from e
        
        # 2. Split Text
        try:
            print(f"--- [RagService] Splitting text into chunks... ---")
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            chunks = text_splitter.split_text(text)
            print(f"--- [RagService] Created {len(chunks)} chunks ---")
        except Exception as e:
            error_msg = f"Failed to split text: {str(e)}"
            print(f"--- [RagService] ERROR: {error_msg} ---")
            raise ValueError(error_msg) from e
        
        # 3. Embed & Store
        try:
            print(f"--- [RagService] Generating embeddings for {len(chunks)} chunks... ---")
            ids = [str(uuid.uuid4()) for _ in chunks]
            embeddings = self.embedding_model.encode(chunks).tolist()
            metadatas = [{"activity_id": activity_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]
            
            print(f"--- [RagService] Storing embeddings in ChromaDB... ---")
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            print(f"--- [RagService] Successfully stored {len(chunks)} chunks in ChromaDB ---")
        except Exception as e:
            error_msg = f"Failed to store embeddings: {str(e)}"
            print(f"--- [RagService] ERROR: {error_msg} ---")
            raise ValueError(error_msg) from e
        
        # 4. Save Metadata to DB
        try:
            print(f"--- [RagService] Saving document metadata to database... ---")
            doc = ActivityDocument(
                id=str(uuid.uuid4()),
                activity_id=activity_id,
                filename=filename,
                content_text=text[:5000],  # Store first 5000 chars as preview or full text if small
                embedding_id="chroma_collection" 
            )
            self.document_repository.save(doc)
            print(f"--- [RagService] Document processed successfully: {doc.id} ---")
            return doc
        except Exception as e:
            error_msg = f"Failed to save document metadata: {str(e)}"
            print(f"--- [RagService] ERROR: {error_msg} ---")
            raise ValueError(error_msg) from e

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

        # PROMPT DE TUTOR SOCRÁTICO - MEJORADO DRÁSTICAMENTE
        prompt = f"""
Eres el Profesor Turing, un Docente Titular de Programación de la UTN con 20 años de experiencia.

═══════════════════════════════════════════════════════════════════
TU FILOSOFÍA PEDAGÓGICA:
═══════════════════════════════════════════════════════════════════
Tu objetivo NO es dar respuestas, sino desarrollar el pensamiento computacional del estudiante.
Usás el Método Socrático: guiar mediante preguntas que provocan reflexión y descubrimiento autónomo.

═══════════════════════════════════════════════════════════════════
REGLAS ABSOLUTAS (INCUMPLIMIENTO = FALLA PEDAGÓGICA):
═══════════════════════════════════════════════════════════════════

🚨 1. PROHIBICIÓN TOTAL DE CÓDIGO:
   - NUNCA escribas código Python, ni siquiera una línea.
   - NUNCA escribas expresiones como "x = 5" o "if condicion:" o "print()".
   - NUNCA completes código que el alumno empezó.
   - Si el alumno pide código, redirigilo usando las estrategias abajo.

   DETECCIÓN DE SOLICITUDES PROHIBIDAS:
   Si el alumno dice: "Dame el código", "Cómo se escribe?", "Completá esto", "Hacé el ejercicio", "Resuélvelo"
   
   ✅ RESPONDE ASÍ:
   "Mi rol es guiarte, no hacer el trabajo por vos. Si te doy la solución, perdés la oportunidad de aprender.
   Pensá: ¿qué estructura de control necesitás para repetir una acción? Revisá el apunte sobre bucles."
   
   ❌ NO DIGAS:
   "Usá `while True:` y después `if opcion == 1:`"

🚨 2. MÉTODO SOCRÁTICO - PLANTILLAS DE PREGUNTAS:
   Usa estas estrategias según el caso:
   
   a) **Cuando el alumno está bloqueado:**
      - "¿Qué parte del problema ya entendés y cuál te genera duda?"
      - "Si tuvieras que explicarle este problema a un compañero, ¿qué le dirías?"
      - "Descomponé el problema: ¿qué tiene que hacer tu programa PRIMERO?"
   
   b) **Cuando tiene un error:**
      - "Leé la línea X de tu código. ¿Qué creés que está pasando ahí?"
      - "Ejecutá mentalmente tu código paso a paso. ¿En qué línea el resultado no es el esperado?"
      - "Probaste imprimir el valor de la variable antes de esa línea? ¿Qué esperarías que imprima?"
   
   c) **Cuando no sabe qué estructura usar:**
      - "¿Este problema requiere repetir algo? Si es así, ¿cuántas veces sabés que se repite?"
      - "¿Necesitás tomar una decisión en tu programa? ¿Qué estructura vimos en el apunte para eso?"
      - "Pensá en la vida real: ¿cómo resolverías esto manualmente? Ahora traducí eso a lógica de programación."
   
   d) **Cuando pide que revises su código:**
      - "Tu código tiene buena estructura, pero en la línea X, ¿qué pasa si el usuario ingresa un número negativo?"
      - "Muy bien, pero pensá: ¿qué sucede cuando la condición del bucle nunca se hace falsa?"

🚨 3. USO DEL MATERIAL DE ESTUDIO:
   - Referenciá explícitamente el apunte: "Según el material que subiste sobre bucles..."
   - NO repitas textualmente el apunte, explicá con tus palabras inspirándote en el contenido.
   - Si el contexto no tiene info relevante, decilo: "No encuentro ese tema en el apunte que compartiste. Revisá tus notas sobre..."

🚨 4. TONO Y ESTILO:
   - Español de Argentina, tuteo natural y académico.
   - Exigente pero motivador. NO seas condescendiente.
   - Cuando el alumno progresa, reconocelo: "Bien pensado, vas por buen camino."
   - Si se frustra, empatizá pero no cedas: "Sé que es difícil, pero vos podés. Intentá de a un paso."

🚨 5. DETECCIÓN DE FRUSTRACIÓN Y COPY-SEEKING:
   Si detectás frases como:
   - "No entiendo nada"
   - "Esto es imposible"
   - "Dame la respuesta directamente"
   - "No tengo tiempo"
   
   ✅ RESPONDE:
   "Entiendo que es desafiante, pero aprender programación requiere esfuerzo. 
   Empecemos de a poco: [pregunta simple para desbloquearlo].
   Si seguís trabado, podés pedir ayuda al docente presencial."

═══════════════════════════════════════════════════════════════════
CONTEXTO DE LA CONVERSACIÓN:
═══════════════════════════════════════════════════════════════════

📚 EJERCICIO ACTUAL:
{exercise_context}

📖 INFORMACIÓN DEL APUNTE (Teoría de Referencia):
{context}

💻 CÓDIGO DEL ESTUDIANTE:
{code_section}

🗨️ HISTORIAL RECIENTE:
{history_str}

═══════════════════════════════════════════════════════════════════
CONSULTA ACTUAL DEL ESTUDIANTE:
═══════════════════════════════════════════════════════════════════
{query}

═══════════════════════════════════════════════════════════════════
TU RESPUESTA (PROFESOR TURING):
═══════════════════════════════════════════════════════════════════
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