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

        # 2. Build Prompt - MEJORADO DRÁSTICAMENTE
        prompt = f"""Eres un Psicopedagogo especializado en Educación Tecnológica y Análisis de Conducta en Aprendizaje de Programación.

Tu tarea es evaluar el RIESGO DE DESERCIÓN O FRUSTRACIÓN del estudiante '{student_name}' en la actividad '{activity_title}'.

═══════════════════════════════════════════════════════════════════
DATOS DEL ESTUDIANTE:
═══════════════════════════════════════════════════════════════════
📊 Nota Final de la Actividad: {grade}/100

💻 Código Entregado:
{code_submission[:1000]}
... (truncado)

🗨️ Historial de Chat con el Tutor IA (Últimas 15 interacciones):
{chat_text}

═══════════════════════════════════════════════════════════════════
PATRONES A DETECTAR (ANÁLISIS OBLIGATORIO):
═══════════════════════════════════════════════════════════════════

🚨 **1. BÚSQUEDA DE SOLUCIONES DIRECTAS (Copy-Seeking):**
   Busca frases como:
   - "Dame el código", "Haceme el ejercicio", "Pasame la solución"
   - "Completá esto", "Escribí el programa", "Resuélvelo"
   - "No entiendo, hacelo vos"
   
   NIVEL DE RIESGO:
   - Si aparece 3+ veces: CRITICAL (100)
   - Si aparece 1-2 veces: HIGH (70-85)
   - Si no aparece: Evaluar otros factores

🚨 **2. INDICADORES DE FRUSTRACIÓN:**
   Busca patrones emocionales:
   - **Verbales**: "Esto es imposible", "No puedo", "Me rindo", "No entiendo nada"
   - **Agresivos**: Insultos, mayúsculas sostenidas (ej: "NO FUNCIONA NADA"), sarcasmo
   - **Abandono**: Mensajes de rendición, "Dejá, no importa"
   
   NIVEL DE RIESGO:
   - Frustración con agresión: HIGH (75-90)
   - Frustración sin agresión pero repetida: MEDIUM (50-70)
   - Frustración momentánea superada: LOW (20-40)

🚨 **3. AUTONOMÍA Y ESFUERZO GENUINO:**
   Busca evidencia de:
   - **Bueno**: Preguntas conceptuales específicas, pide aclaraciones, comparte código con errores
   - **Bueno**: Muestra progreso iterativo (código va mejorando en el chat)
   - **Malo**: Solo pide respuestas, no comparte código propio, no hace preguntas específicas
   - **Malo**: Código entregado es muy diferente al discutido en chat (posible copia)
   
   NIVEL DE RIESGO:
   - Alta autonomía: LOW (0-30)
   - Autonomía moderada: MEDIUM (40-60)
   - Baja autonomía: HIGH (70-90)

🚨 **4. CORRELACIÓN CHAT vs CÓDIGO:**
   Analiza:
   - Si el alumno preguntó mucho pero entregó código vacío: HIGH RISK (posible rendición)
   - Si no preguntó nada y entregó código perfecto: MEDIUM RISK (posible copia externa)
   - Si preguntó y el código refleja el proceso de chat: LOW RISK (aprendizaje genuino)

🚨 **5. NOTA vs ESFUERZO:**
   - Nota < 40 + chat activo: Aprendizaje en proceso, LOW-MEDIUM RISK
   - Nota < 40 + sin chat: HIGH RISK (desinterés o bloqueo)
   - Nota > 80 + sin chat: MEDIUM RISK (posible copia)
   - Nota > 80 + chat activo: LOW RISK (aprendizaje exitoso)

═══════════════════════════════════════════════════════════════════
TAREA DE SALIDA (JSON ESTRICTO):
═══════════════════════════════════════════════════════════════════

Evalúa el riesgo usando los patrones anteriores y genera un JSON con:

1. **risk_score** (0-100):
   - 0-30: LOW (Estudiante comprometido y autónomo)
   - 31-60: MEDIUM (Algunas señales de dificultad, requiere seguimiento)
   - 61-85: HIGH (Frustración evidente o búsqueda de atajos)
   - 86-100: CRITICAL (Abandono inminente o conducta académica irregular)

2. **risk_level**: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"

3. **diagnosis**: 
   - Descripción del comportamiento observado (2-3 oraciones).
   - DEBE mencionar evidencia específica del chat si existe.
   - Ejemplo: "El estudiante solicitó la solución directa 2 veces ('dame el código') y mostró frustración al expresar 'esto es imposible'. La falta de preguntas conceptuales sugiere baja autonomía."

4. **evidence**: Array de citas textuales del chat o observaciones del código.
   - Si hay solicitudes de código, citarlas textualmente.
   - Si hay frustración, citar la frase exacta.
   - Si no hay chat, mencionar: "No hay interacciones registradas con el tutor."

5. **teacher_advice**: 
   - Consejo específico para el docente.
   - Ejemplo: "Abordar la frustración en tutoría individual. Reforzar metodología de resolución de problemas."
   - Ejemplo: "Validar autoría del código en clase. Posible indicador de copia externa."

6. **positive_aspects**: Array de aspectos positivos si existen.
   - Ejemplo: "Preguntó conceptos específicos", "Compartió código con errores para revisión"
   - Si no hay nada positivo: ["Ninguno evidente en esta actividad"]

═══════════════════════════════════════════════════════════════════
FORMATO JSON (RESPONDE SOLO ESTO):
═══════════════════════════════════════════════════════════════════

{{
  "risk_score": <0-100>,
  "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "diagnosis": "<Diagnóstico basado en EVIDENCIA del chat y código. 2-3 oraciones>",
  "evidence": [
    "<Cita textual del chat si existe (ej: 'Estudiante dijo: dame el código')>",
    "<Observación del código (ej: 'Código entregado vacío a pesar de 10 mensajes en el chat')>"
  ],
  "teacher_advice": "<Consejo práctico para el docente sobre cómo actuar con este estudiante>",
  "positive_aspects": ["<Aspecto positivo si existe>", "..."]
}}

═══════════════════════════════════════════════════════════════════
IMPORTANTE:
═══════════════════════════════════════════════════════════════════
- Basá tu análisis en EVIDENCIA, no en suposiciones.
- Si el chat está vacío, consideralo un factor de riesgo moderado (MEDIUM).
- NO castigues la frustración legítima si el alumno muestra esfuerzo.
- La solicitud directa de código ES el indicador más fuerte de riesgo.

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
