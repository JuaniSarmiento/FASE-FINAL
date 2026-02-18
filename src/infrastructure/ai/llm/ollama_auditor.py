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

        prompt = f"""Actúas como un estricto Profesor Senior de Programación de la UTN.
Tu tarea es auditar y calificar una entrega de ejercicios.

LISTADO DE EJERCICIOS A EVALUAR:
{exercises_text}

INSTRUCCIONES DE EVALUACIÓN (CRITICAS):
1. **Detección de Código Vacío**: Si el código dice "[CÓDIGO VACÍO / NO INTENTADO]" o solo tiene comentarios, la nota **DEBE SER 0** y el feedback debe decir "No se ha entregado código".
2. **Sin Alucinaciones**: No inventes que el código funciona si está vacío. Si no hay lógica implementada, no hay puntos.
3. **Funcionalidad**: Evalúa si el código realmente resuelve el problema (si el título dice "Bucle While" y no hay bucle, baja la nota).
4. **Nota**: 
   - 0 para vacío.
   - 1-40 para intentos fallidos o incompletos.
   - 60+ solo si funciona.
   - 90+ solo si es perfecto y optimizado.

IMPORTANTE:
- Responde ÚNICAMENTE con un JSON válido.
- El formato debe ser EXACTAMENTE el siguiente:

IMPORTANTE:
- Responde ÚNICAMENTE con un JSON válido.
- No incluyas texto antes ni después del JSON (nada de "Aquí tienes el JSON...").
- El formato debe ser EXACTAMENTE el siguiente:

{{
  "final_grade": <promedio numérico>,
  "general_feedback": "<Resumen general>",
  "exercises_audit": [
    {{
      "exercise_id": "<id del ejercicio si está disponible, sino usar índice o título>",
      "title": "<título>",
      "grade": <nota 0-100>,
      "passed": <true/false>,
      "feedback": "<Explicación técnica detallada>"
    }}
  ]
}}
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