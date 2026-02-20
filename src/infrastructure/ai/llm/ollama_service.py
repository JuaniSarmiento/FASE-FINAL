import requests
import json
from typing import List
from src.application.learning.ports.exercise_generator import IExerciseGenerator
from src.domain.learning.entities.exercise import Exercise, TestCase
from src.domain.learning.value_objects.difficulty import Difficulty
from src.domain.learning.value_objects.programming_language import ProgrammingLanguage
from src.domain.learning.value_objects.exercise_status import ExerciseStatus
from src.infrastructure.config.settings import settings

class OllamaExerciseGenerator(IExerciseGenerator):
    def __init__(self):
        # List of potential URLs to try
        self.potential_urls = [
            "http://187.77.41.214:11434",
            settings.OLLAMA_BASE_URL.rstrip("/"),
            "http://host.docker.internal:11434",
            "http://172.17.0.1:11434", # Default Docker bridge gateway
            "http://ollama:11434", # If running in a container named 'ollama'
            "http://localhost:11434"
        ]
        self.base_url = None
        # FIX 1: Apuntamos al modelo más inteligente que bajamos (3B)
        self.model = "llama3" 

    def _find_working_url(self):
        if self.base_url:
            return self.base_url
            
        print("--- [Ollama] Finding working Ollama URL... ---")
        for url in self.potential_urls:
            try:
                # Use /api/tags or /api/version to check connectivity lightly
                resp = requests.get(f"{url}/api/tags", timeout=1)
                if resp.status_code == 200:
                    print(f"--- [Ollama] Connected successfully to {url} ---")
                    self.base_url = url
                    return url
            except Exception:
                print(f"--- [Ollama] Failed to connect to {url} ---")
                continue
        
        # Fallback to settings if none work (will likely fail but keeps original behavior)
        print("--- [Ollama] Could not find working URL, defaulting to settings ---")
        return settings.OLLAMA_BASE_URL.rstrip("/")

    def generate(
        self, 
        topic: str, 
        count: int, 
        difficulty: Difficulty, 
        language: ProgrammingLanguage,
        context: str = None
    ) -> List[Exercise]:
        
        base_url = self._find_working_url()
        all_exercises = []
        remaining = count
        batch_size = 1 # Generate one by one to maximize stability with small LLMs
        
        print(f"--- [OllamaExerciseGenerator] Requested {count} exercises. Strategy: Batches of {batch_size}. ---")

        while remaining > 0:
            current_batch_size = min(batch_size, remaining)
            print(f"--- [OllamaExerciseGenerator] Generating batch of {current_batch_size} exercises for topic '{topic}'... ---")
            
            prompt = self._build_prompt(topic, current_batch_size, difficulty, language, context)
            
            try:
                url = f"{base_url}/api/generate"
                
                response = requests.post(
                    url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json", # Ollama JSON mode
                        "options": {
                            "temperature": 0.1, # FIX 2: Temperatura bajísima para forzar estructura lógica y no creativa
                            "top_p": 0.9
                        }
                    },
                    timeout=300 # Timeout per batch
                )
                
                if response.status_code != 200:
                    print(f"--- [OllamaExerciseGenerator] HTTP ERROR {response.status_code}: {response.text} ---")
                    if response.status_code == 404:
                         print(f"--- [OllamaExerciseGenerator] HINT: Model '{self.model}' might be missing. Try 'ollama pull {self.model}' ---")
                    break
                
                response.raise_for_status()
                result = response.json()
                raw_response = result['response']
                
                # FIX 3: Limpiador de JSON por si la IA mete basura antes de la primera llave
                start_idx = raw_response.find('{')
                end_idx = raw_response.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    clean_json_str = raw_response[start_idx:end_idx]
                else:
                    clean_json_str = raw_response

                generated_data = json.loads(clean_json_str)
                
                batch_exercises = []
                for item in generated_data.get('exercises', []):
                    batch_exercises.append(self._map_json_to_exercise(item, difficulty, language))
                
                print(f"--- [OllamaExerciseGenerator] Batch success: {len(batch_exercises)} exercises parsed ---")
                all_exercises.extend(batch_exercises)
                remaining -= current_batch_size
                
            except Exception as e:
                print(f"--- [OllamaExerciseGenerator] EXCEPTION in batch: {e} ---")
                if not all_exercises:
                    raise e
                else:
                    print("--- [OllamaExerciseGenerator] Returning partial results due to error ---")
                    break

        print(f"--- [OllamaExerciseGenerator] Total generated: {len(all_exercises)}/{count} ---")
        return all_exercises

    def _build_prompt(self, topic: str, count: int, difficulty: Difficulty, language: ProgrammingLanguage, context: str = None) -> str:
        # FIX 4: Prompt con rol educativo y constraints narrativos fuertes
        base_prompt = f"""
        Eres un Diseñador Instruccional experto en crear ejercicios de programación para estudiantes universitarios.
        Tu misión es generar {count} ejercicio(s) de programación sobre el tema '{topic}'.
        
        Parámetros:
        - Dificultad: {difficulty.value}
        - Lenguaje: {language.value}

        REGLAS ESTRICTAS DE GENERACIÓN:
        1. IDIOMA: Todo el texto (títulos, enunciados, comentarios del código) debe estar en Español de Argentina.
        2. NARRATIVA ACADÉMICA: El 'problem_statement' debe plantear un caso de uso real e interesante (ej. simular un cajero automático, calcular el promedio de notas de la UTN).
        3. NIVEL PRINCIPIANTE (SIN FUNCIONES): El estudiante NO SABE qué es una función. El 'starter_code' debe ser un script de arriba hacia abajo. NO uses "def" ni "class".
        4. CASOS DE PRUEBA: Los 'test_cases' deben tener inputs simples (en formato string) y la salida esperada exacta. Deben ser lógicos para el problema.

        FORMATO OBLIGATORIO:
        Devuelve ÚNICAMENTE un objeto JSON válido. Nada de texto introductorio. Usa esta estructura exacta:
        {{
            "exercises": [
                {{
                    "title": "Nombre del Ejercicio",
                    "problem_statement": "Descripción narrativa del problema y las instrucciones exactas de qué debe hacer el programa...",
                    "starter_code": "# Escribe tu código aquí\n",
                    "test_cases": [
                        {{"input_data": "10", "expected_output": "20", "is_hidden": false}},
                        {{"input_data": "5", "expected_output": "10", "is_hidden": true}}
                    ]
                }}
            ]
        }}
        """
        
        if context:
            base_prompt += f"\n\nATENCIÓN: Integra la siguiente INFORMACIÓN DEL APUNTE como temática para el ejercicio. Adapta la narrativa del problema a este contexto:\n---\n{context}\n---\n"
        
        return base_prompt

    def _map_json_to_exercise(self, data: dict, difficulty: Difficulty, language: ProgrammingLanguage) -> Exercise:
        import uuid
        test_cases = [
            TestCase(
                input_data=tc.get('input_data', ''),
                expected_output=tc.get('expected_output', ''),
                is_hidden=tc.get('is_hidden', False)
            ) for tc in data.get('test_cases', [])
        ]
        
        return Exercise(
            id=str(uuid.uuid4()), # Partial ID, ActivityID set by UseCase
            activity_id="TEMP", # Will be overwritten by UseCase
            title=data.get('title', 'Untitled'),
            problem_statement=data.get('problem_statement', ''),
            starter_code=data.get('starter_code', ''),
            solution_code=data.get('solution_code', ''),
            difficulty=difficulty,
            language=language,
            status=ExerciseStatus.DRAFT,
            test_cases=test_cases
        )