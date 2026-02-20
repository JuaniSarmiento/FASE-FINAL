import requests
import json
import os
from typing import List, Dict, Any
from src.domain.grading.ports.ai_auditor import IAiAuditor
from src.infrastructure.config.settings import settings

class OllamaAuditor(IAiAuditor):
    def __init__(self):
        # List of potential URLs to try, similar to ExerciseGenerator
        self.potential_urls = [
            "http://187.77.41.214:11434",
            settings.OLLAMA_BASE_URL.rstrip("/"),
            "http://host.docker.internal:11434",
            "http://172.17.0.1:11434", 
            "http://ollama:11434", 
            "http://localhost:11434"
        ]
        self.base_url = None
        # FIX 1: Unificamos el modelo a llama3.2 para no reventar la RAM
        self.model = "llama3" 

    def _find_working_url(self):
        if self.base_url:
            return self.base_url
        for url in self.potential_urls:
            try:
                resp = requests.get(f"{url}/api/tags", timeout=1)
                if resp.status_code == 200:
                    self.base_url = url
                    return url
            except Exception:
                continue
        return settings.OLLAMA_BASE_URL.rstrip("/")

    def audit_activity(self, exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
        base_url = self._find_working_url()
        
        exercises_text = ""
        for i, ex in enumerate(exercises):
            # Check if code is empty or just comments/whitespace
            raw_code = ex.get('code', '').strip()
            is_empty = not raw_code or raw_code == ""
            
            code_display = "[CÓDIGO VACÍO / NO INTENTADO]" if is_empty else raw_code[:1500]
            
            status_text = "✅ CORRECTO" if ex.get('passed') else "❌ INCORRECTO/NO INTENTADO"
            exercises_text += f"\n--- EJERCICIO {i+1} ---\nID: {ex.get('id')}\nTítulo: {ex.get('title')}\nDificultad: {ex.get('difficulty')}\nCódigo del Estudiante:\n{code_display}\n---------------------\n"

        prompt = f"""Eres un Profesor Senior de Programación de la UTN con experiencia en evaluación formativa.
Tu tarea es auditar y calificar una entrega de ejercicios de programación con CRITERIO PEDAGÓGICO.

═══════════════════════════════════════════════════════════════════
EJERCICIOS A EVALUAR:
═══════════════════════════════════════════════════════════════════
{exercises_text}

═══════════════════════════════════════════════════════════════════
CRITERIOS DE EVALUACIÓN (APLICAR CON RIGOR):
═══════════════════════════════════════════════════════════════════

🔍 **1. DETECCIÓN DE CÓDIGO VACÍO O NO INTENTADO:**
   - Si el código dice "[CÓDIGO VACÍO / NO INTENTADO]" o solo contiene comentarios sin lógica:
     * Nota: 0/100
     * Feedback: "No se ha entregado código. Es necesario implementar la solución para ser evaluado."
   - Si hay import/variables pero sin lógica funcional:
     * Nota: 0-20/100
     * Feedback: "El código está incompleto. Falta implementar la lógica principal del problema."

🔍 **2. FUNCIONALIDAD Y CORRECTITUD:**
   - ¿El código resuelve el problema planteado?
   - ¿Maneja todos los casos de prueba (inputs válidos, inválidos, edge cases)?
   - ¿La salida coincide con lo esperado en el enunciado?
   
   Escala de Notas:
   - 0-20: No funciona o vacío
   - 21-40: Intento fallido, lógica incorrecta
   - 41-59: Funciona parcialmente, faltan casos o tiene errores
   - 60-75: Funciona pero con errores menores o código mejorable
   - 76-89: Funciona correctamente, código limpio
   - 90-100: Perfecto, código óptimo y elegante

🔍 **3. CALIDAD DEL CÓDIGO:**
   Evalúa:
   - **Legibilidad**: ¿Usa nombres de variables descriptivos? ¿Tiene buena indentación?
   - **Eficiencia**: ¿Hay bucles innecesarios? ¿Usa estructuras adecuadas?
   - **Buenas prácticas**: ¿Evita repetición de código? ¿Valida inputs?
   - **Simplicidad**: ¿Es el código tan simple como podría ser?

🔍 **4. FEEDBACK TÉCNICO DETALLADO (OBLIGATORIO):**
   Para CADA ejercicio, proporciona:
   
   a) **Si el código funciona:**
      - Reconoce los aciertos específicos (ej: "Excelente uso del bucle while para validar input")
      - Sugiere mejoras concretas (ej: "Podrías usar una lista en lugar de 5 variables separadas")
      - Menciona edge cases no manejados si existen
   
   b) **Si el código NO funciona:**
      - Identifica el error principal (ej: "La condición del if en línea X siempre es False porque...")
      - Sugiere el concepto a revisar (ej: "Revisá operadores de comparación en Python")
      - NO des la solución completa, pero señala dónde buscar
   
   c) **Si está vacío:**
      - "No se ha entregado código. Intentá implementar al menos la estructura básica del problema."

🔍 **5. NOTA FINAL (PROMEDIO):**
   - Calcula el promedio aritmético de todas las notas individuales.
   - Si todos los ejercicios están vacíos, la nota final es 0.
   - Redondea a 2 decimales.

═══════════════════════════════════════════════════════════════════
FORMATO DE SALIDA (JSON ESTRICTO):
═══════════════════════════════════════════════════════════════════

Responde ÚNICAMENTE con un JSON válido. Sin texto antes ni después.
Estructura EXACTA:

{{
  "final_grade": <número 0-100, promedio de todos los ejercicios>,
  "general_feedback": "<Resumen general de la entrega: fortalezas, debilidades, consejo principal para mejorar>",
  "exercises_audit": [
    {{
      "exercise_id": "<id del ejercicio o su índice>",
      "title": "<título del ejercicio>",
      "grade": <nota 0-100>,
      "passed": <true si grade >= 60, false en caso contrario>,
      "feedback": "<Análisis técnico detallado: qué está bien, qué está mal, cómo mejorar. Mínimo 2 oraciones.>"
    }}
  ]
}}

═══════════════════════════════════════════════════════════════════
IMPORTANTE:
═══════════════════════════════════════════════════════════════════
- NO inventes que el código funciona si está vacío o incompleto.
- Sé ESTRICTO pero CONSTRUCTIVO en tus evaluaciones.
- El feedback debe ayudar al alumno a mejorar, no solo señalar errores.
- Si un ejercicio resuelve el problema de forma poco elegante pero funciona, la nota debe ser 65-75, no 90.

"""
        
        try:
            url = f"{base_url}/api/generate"
            response = requests.post(
                url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.0, # Deterministic structure
                        "num_predict": 1024
                    }
                },
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"Ollama Error {response.status_code}: {response.text}")
                return self._fallback_response(f"Error AI: {response.text}")

            result = response.json()
            raw_response = result.get('response', '{}')
            
            # Robust JSON cleaning
            try:
                # Find first { and last }
                start = raw_response.find('{')
                end = raw_response.rfind('}')
                if start != -1 and end != -1:
                    json_str = raw_response[start:end+1]
                    audit_data = json.loads(json_str)
                    
                    # Ensure all keys exist
                    if "exercises_audit" not in audit_data:
                        audit_data["exercises_audit"] = []
                        
                    return audit_data
                else:
                    print(f"Invalid JSON response format: {raw_response}")
                    return self._fallback_response("Formato JSON inválido de la IA.")
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e} - Response: {raw_response}")
                return self._fallback_response("Error al decodificar respuesta de IA.")
                
        except Exception as e:
            print(f"Error calling Ollama Auditor: {e}")
            return self._fallback_response(f"Excepción interna: {str(e)}")

    def _fallback_response(self, error: str) -> Dict[str, Any]:
        return {
            "final_grade": 0,
            "general_feedback": f"Evaluación automática no disponible: {error}",
            "exercises_audit": []
        }