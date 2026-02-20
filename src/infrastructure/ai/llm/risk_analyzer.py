import os
import json
import logging
import requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    def __init__(self, model: str = None, base_url: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://187.77.41.214:11434")

    def analyze_student_risk(self, student_name: str, activity_title: str, chat_history: List[Dict], code_submission: str, grade: float) -> Dict[str, Any]:
        """
        Analyzes student risk based on chat history and submission.
        """
        
        # 1. Format Chat History
        chat_text = ""
        if not chat_history:
            chat_text = "No hay interacciones de chat registradas."
        else:
            for msg in chat_history[-15:]: # Last 15 messages
                role = "Estudiante" if msg.get('role') == 'user' else "IA Tutor"
                chat_text += f"{role}: {msg.get('content')}\n"

        # 2. Build Prompt
        prompt = f"""Actúas como un Psicólogo Educativo y Experto en Pedagogía de Programación.
Analiza el desempeño y comportamiento del estudiante '{student_name}' en la actividad '{activity_title}'.

DATOS:
- Nota Final: {grade}/100
- Código Entregado:
{code_submission[:1000]}
... (truncado)

- Historial de Chat con el Tutor IA:
{chat_text}

TAREA:
Evalúa el "Riesgo de Deserción o Frustración" y detecta patrones de aprendizaje.
Busca explícitamente en el chat:
1. **Solicitud de Código**: ¿El estudiante pidió la solución directa ("dame el código", "resuélvelo")?
2. **Frustración/Conducta**: ¿Hubo insultos, mayúsculas agresivas o abandono?
3. **Autonomía**: ¿Preguntó dudas conceptuales o solo copió y pegó?

SALIDA REQUERIDA (JSON):
{{
  "risk_score": <0-100, donde 100 es riesgo crítico>,
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "diagnosis": "<Diagnóstico que MENCIONE el comportamiento en el chat (ej: 'Se frustró y pidió código')>",
  "evidence": ["<Cita textual del chat si hubo conducta relevante>", "<Evidencia de código>"],
  "teacher_advice": "<Consejo basado en comportamiento (ej: 'Abordar la frustración con el alumno')>",
  "positive_aspects": ["<Algo bueno>"]
}}

Responde SOLO el JSON.
"""

        try:
            url = f"{self.base_url}/api/generate"
            response = requests.post(
                url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.2
                    }
                },
                timeout=60
            )

            if response.status_code != 200:
                logger.error(f"Ollama Risk Analysis Failed: {response.text}")
                return self._fallback_risk()

            result = response.json()
            raw_response = result.get('response', '{}')
            
            # Parse JSON
            try:
                start = raw_response.find('{')
                end = raw_response.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(raw_response[start:end+1])
                else:
                    return self._fallback_risk("Error de formato JSON")
            except Exception:
                return self._fallback_risk("Error de parsing JSON")

        except Exception as e:
            logger.error(f"Risk Analysis Exception: {e}")
            return self._fallback_risk(str(e))

    def _fallback_risk(self, reason: str = "") -> Dict[str, Any]:
        return {
            "risk_score": 0,
            "risk_level": "LOW",
            "diagnosis": "No se pudo realizar el análisis automático.",
            "evidence": [f"Error interno: {reason}"],
            "teacher_advice": "Revise manualmente la entrega.",
            "positive_aspects": []
        }
