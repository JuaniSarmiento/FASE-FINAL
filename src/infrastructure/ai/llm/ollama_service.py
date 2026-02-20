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
        # List of potential URLs to try - Prioritize external IP first
        self.potential_urls = [
            "http://187.77.41.214:11434",  # External Ollama server
            settings.OLLAMA_BASE_URL.rstrip("/"),
            "http://host.docker.internal:11434",
            "http://ollama:11434", # If running in Docker with service name
            "http://172.17.0.1:11434", # Default Docker bridge gateway
            "http://localhost:11434", # Local development
        ]
        self.base_url = None
        self.model = "llama3"
        print(f"--- [OllamaExerciseGenerator] Initialized with model: {self.model} ---") 

    def _find_working_url(self):
        if self.base_url:
            return self.base_url
            
        print("--- [Ollama] Finding working Ollama URL... ---")
        for url in self.potential_urls:
            try:
                # Use /api/tags or /api/version to check connectivity lightly
                resp = requests.get(f"{url}/api/tags", timeout=2)
                if resp.status_code == 200:
                    print(f"--- [Ollama] Connected successfully to {url} ---")
                    # Verify model is available
                    tags_data = resp.json()
                    available_models = [model.get('name', '').split(':')[0] for model in tags_data.get('models', [])]
                    print(f"--- [Ollama] Available models: {available_models} ---")
                    if self.model not in available_models and not any(self.model in m for m in available_models):
                        print(f"--- [Ollama] WARNING: Model '{self.model}' not found. Available: {available_models} ---")
                        print(f"--- [Ollama] HINT: Run 'ollama pull {self.model}' to download the model ---")
                    self.base_url = url
                    return url
            except Exception as e:
                print(f"--- [Ollama] Failed to connect to {url}: {str(e)} ---")
                continue
        
        # No working URL found
        error_msg = f"Could not connect to Ollama at any URL. Tried: {self.potential_urls}"
        print(f"--- [Ollama] CRITICAL ERROR: {error_msg} ---")
        raise ConnectionError(error_msg)

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
        # PROMPT MEJORADO DRÁSTICAMENTE - Sin código en starter_code, ejercicios únicos y variados
        base_prompt = f"""
Eres un Diseñador Instruccional Senior de la UTN especializado en crear ejercicios de programación pedagógicamente efectivos.

MISIÓN: Generar {count} ejercicio(s) ÚNICOS Y VARIADOS sobre el tema '{topic}'.

PARÁMETROS:
- Dificultad: {difficulty.value}
- Lenguaje: {language.value}

═══════════════════════════════════════════════════════════════════
REGLAS CRÍTICAS (CUMPLIMIENTO OBLIGATORIO):
═══════════════════════════════════════════════════════════════════

1. **IDIOMA**: Español de Argentina en todo el contenido (títulos, enunciados, comentarios).

2. **DIVERSIDAD ABSOLUTA**: 
   - Cada ejercicio DEBE tener un escenario COMPLETAMENTE DIFERENTE.
   - PROHIBIDO repetir temas (ej: si ya hiciste "Cajero Automático", NO hagas "Cajero Bancario" ni "ATM").
   - Usa contextos variados: tiendas, juegos, universidad, clima, deportes, cocina, etc.
   - Ejemplo de VARIEDAD CORRECTA: "Cajero Automático", "Calculadora de Notas UTN", "Sistema de Descuentos en Tienda", "Juego de Adivinanzas".

3. **TÍTULOS DESCRIPTIVOS**: 
   - NUNCA uses "Untitled", "Sin Título" o "Ejercicio N".
   - El título debe describir claramente el problema (ej: "Calculadora de Promedio de Notas", "Conversor de Temperatura").

4. **STARTER_CODE - REGLA MÁS IMPORTANTE**:
   🚨 ATENCIÓN: El campo "starter_code" DEBE contener ÚNICAMENTE este texto exacto:
   
   "# Escribe tu código aquí\n"
   
   ❌ PROHIBIDO ABSOLUTAMENTE:
   - NO incluyas variables declaradas (ej: "saldo = 0")
   - NO incluyas bucles (ej: "while True:")
   - NO incluyas input() o print()
   - NO incluyas lógica condicional (ej: "if opcion == 1:")
   - NO incluyas ninguna línea de código excepto el comentario
   
   ✅ CORRECTO: "# Escribe tu código aquí\n"
   ❌ INCORRECTO: "# Escribe tu código aquí\nsaldo = 0\n"
   ❌ INCORRECTO: "# Declara las variables aquí\n"

5. **PROBLEM_STATEMENT** (Enunciado del Problema):
   - Debe ser una narrativa clara y detallada que describa:
     * El contexto del problema (ej: "Sos el encargado de una librería...")
     * Qué debe hacer el programa paso a paso
     * Qué inputs recibirá y qué outputs debe generar
     * Ejemplos de ejecución si es necesario
   - Longitud recomendada: 3-6 oraciones.

6. **TEST_CASES** (Casos de Prueba):
   - Mínimo 2 casos de prueba por ejercicio (1 visible, 1 oculto).
   - El "input_data" debe ser un string simple (ej: "10", "15.5", "Juan").
   - El "expected_output" debe ser EXACTAMENTE lo que el programa debe imprimir.
   - Deben ser lógicos y verificables.

7. **NIVEL DE DIFICULTAD**:
   - BEGINNER: Solo print, input, variables, if/else, bucles básicos (for, while).
   - INTERMEDIATE: Listas, strings avanzados, bucles anidados.
   - ADVANCED: Diccionarios, funciones simples (si el nivel lo permite).
   - NO uses funciones definidas por el usuario si el nivel es BEGINNER.

═══════════════════════════════════════════════════════════════════
FORMATO DE SALIDA (JSON):
═══════════════════════════════════════════════════════════════════

Devuelve ÚNICAMENTE un objeto JSON válido. Sin texto introductorio ni explicaciones.
Estructura EXACTA:

{{
    "exercises": [
        {{
            "title": "Título Descriptivo del Ejercicio",
            "problem_statement": "Descripción narrativa completa del problema con contexto, instrucciones claras de qué debe hacer el programa, qué inputs recibe y qué outputs debe generar. Incluye ejemplos si es necesario para claridad.",
            "starter_code": "# Escribe tu código aquí\\n",
            "test_cases": [
                {{"input_data": "10", "expected_output": "El resultado es: 20", "is_hidden": false}},
                {{"input_data": "5", "expected_output": "El resultado es: 10", "is_hidden": true}}
            ]
        }}
    ]
}}

═══════════════════════════════════════════════════════════════════
EJEMPLOS DE LO QUE NO HACER:
═══════════════════════════════════════════════════════════════════

❌ MALO - Ejercicio repetido:
Ejercicio 1: "Cajero Automático - Depósito"
Ejercicio 2: "Cajero Automático - Retiro"
Ejercicio 3: "Sistema Bancario de Consulta"

❌ MALO - Starter code con solución:
"starter_code": "saldo = 0\\nwhile True:\\n    print('Menú')\\n"

❌ MALO - Título genérico:
"title": "Untitled"
"title": "Ejercicio 3"

✅ BUENO - Ejercicios variados:
Ejercicio 1: "Calculadora de IMC (Índice de Masa Corporal)"
Ejercicio 2: "Simulador de Dados para Juego de Mesa"
Ejercicio 3: "Conversor de Pesos a Dólares"

✅ BUENO - Starter code vacío:
"starter_code": "# Escribe tu código aquí\\n"

✅ BUENO - Título descriptivo:
"title": "Sistema de Descuentos en Supermercado"

═══════════════════════════════════════════════════════════════════
"""
        
        if context:
            base_prompt += f"""
CONTEXTO ADICIONAL DEL APUNTE:
═══════════════════════════════════════════════════════════════════
Integra la siguiente información del material de estudio como temática para los ejercicios.
Adapta la narrativa del problema usando estos conceptos, pero mantén la diversidad de escenarios.

{context}
═══════════════════════════════════════════════════════════════════
"""
        
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