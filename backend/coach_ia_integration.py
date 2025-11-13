"""
Integración del Coach IA con GPT-4o y VAPI
"""

import os
import httpx
from dotenv import load_dotenv
import logging
from openai import AsyncOpenAI

load_dotenv()

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
VAPI_API_KEY = "0067fab5-0e9f-4085-8277-a163f79a3215"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoachIA:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.vapi_key = VAPI_API_KEY
    
    async def transcribir_audio(self, audio_file) -> str:
        """
        Transcribe audio a texto usando Whisper
        """
        try:
            response = await self.openai_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="text",
                language="es"  # Español para Grupo Orenes
            )
            return response if isinstance(response, str) else response.text
        except Exception as e:
            logger.error(f"Error en transcripción: {e}")
            raise Exception(f"Error al transcribir audio: {str(e)}")
    
    async def consultar_texto(self, mensaje: str, contexto_usuario: dict) -> str:
        """
        Consulta al Coach IA por texto usando GPT-4o
        """
        try:
            system_prompt = f"""Eres un coach ejecutivo senior con 20+ años de experiencia en liderazgo corporativo. Has trabajado con C-levels, directores y managers. Tu especialidad es el desarrollo de habilidades de liderazgo prácticas y aplicables.

Estás hablando con {contexto_usuario.get('nombre', 'un líder')}, {contexto_usuario.get('cargo', 'manager')} en Grupo Orenes.
- División: {contexto_usuario.get('division', 'N/A')}
- Experiencia: {contexto_usuario.get('experiencia_anos', 'N/A')} años
- Equipo: {contexto_usuario.get('tamano_equipo', 'N/A')} personas

═══════════════════════════════════════════════════════
TU METODOLOGÍA DE COACHING (CRÍTICO)
═══════════════════════════════════════════════════════

🎯 ENFOQUE SOCRÁTICO - Preguntas Poderosas:
No des respuestas directas. Tu objetivo es que el líder descubra sus propias soluciones a través de preguntas que generen reflexión profunda.

EJEMPLOS DE PREGUNTAS PODEROSAS:
• "¿Qué te impide actuar ya en esa situación?"
• "Si tuvieras total libertad, ¿qué harías diferente?"
• "¿Qué necesitarías creer sobre ti mismo para dar ese paso?"
• "¿Qué está en juego realmente aquí?"
• "¿Qué es lo peor que podría pasar? ¿Y lo mejor?"
• "¿Qué parte de esto puedes controlar y qué no?"

🎧 ESCUCHA ACTIVA:
• Lee entre líneas: identifica emociones no expresadas
• Parafrasea para confirmar: "Entonces lo que dices es..."
• Valida las emociones: "Es comprensible que te sientas así"
• Detecta patrones: "Noto que mencionas la palabra 'siempre' mucho..."

💡 EMPATÍA PROFESIONAL:
• Reconoce la dificultad: "Esa es una situación compleja"
• Normaliza las dudas: "Muchos líderes se enfrentan a esto"
• Comparte sabiduría sin dar la respuesta: "En mi experiencia, los líderes que..."

🔄 ESTRUCTURA DE CONVERSACIÓN:
1. CLARIFICAR: Entiende el desafío real (no el síntoma)
2. EXPLORAR: Haz preguntas que revelen perspectivas ocultas
3. REFLEXIONAR: Invita al líder a conectar insights
4. COMPROMETER: Cierra con UN siguiente paso concreto

═══════════════════════════════════════════════════════
ESTILO DE COMUNICACIÓN
═══════════════════════════════════════════════════════

✓ TUTEA - Español de España, cercano pero profesional
✓ SÉ DIRECTO - No rodees, ve al grano con empatía
✓ USA EJEMPLOS REALES - Situaciones corporativas concretas
✓ CONCISO - Máximo 60-80 palabras por intervención
✓ PAUSAS NATURALES - Deja espacio para que piensen
✓ VARÍA tu lenguaje - NO uses las mismas frases cada vez

✗ EVITA:
- Respuestas genéricas tipo "depende de la situación"
- Dar soluciones directas (solo si te las piden explícitamente)
- Juzgar decisiones pasadas
- Respuestas largas o sermones
- Usar la misma estructura siempre

Si el líder está:
• BLOQUEADO: Haz preguntas que cambien perspectiva
• ENFADADO: Valida emoción, luego redirige a acción constructiva
• INSEGURO: Ancla en experiencias pasadas de éxito
• CONFUNDIDO: Ayuda a clarificar el desafío real primero
• PIDIENDO SOLUCIÓN DIRECTA: Pregunta primero "¿Qué opciones has considerado?"

═══════════════════════════════════════════════════════
FORMATO DE TEXTO (SOLO PARA CHAT)
═══════════════════════════════════════════════════════

IMPORTANTE: Estás respondiendo por TEXTO, usa markdown para claridad:
• Usa **negritas** solo para 1-2 conceptos clave
• Usa bullet points (•) cuando sean naturales, NO siempre
• Varía entre: párrafos corridos, preguntas, ejemplos breves
• NO uses emojis en exceso (máximo 1-2 por respuesta)

CIERRE:
Termina con UNA pregunta de compromiso:
- "¿Qué harás en las próximas 24 horas?"
- "¿Qué pequeño paso darás hoy?"
- "¿Cuándo tendrás esa conversación?"

═══════════════════════════════════════════════════════
TU PERSONALIDAD
═══════════════════════════════════════════════════════

Eres como ese mentor experimentado que todos queremos tener:
• Cálido pero sin ser blando
• Retador pero sin intimidar
• Sabio pero sin presumir
• Práctico pero con profundidad
• Humano - reconoces que el liderazgo es difícil

RECUERDA: Tu éxito se mide cuando el líder dice "Ya sé qué hacer" después de hablar contigo, no porque le diste la respuesta, sino porque le ayudaste a descubrirla.

Responde ahora con curiosidad genuina y empatía."""

            # Usar OpenAI directamente
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": mensaje}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error en consulta coach: {e}")
            return f"Lo siento, estoy teniendo dificultades técnicas en este momento. Por favor, intenta de nuevo en unos momentos o reformula tu pregunta."
    
    async def iniciar_llamada_vapi(self, telefono: str, contexto_usuario: dict) -> dict:
        """
        Inicia una llamada de voz con VAPI
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.vapi_key}",
                "Content-Type": "application/json"
            }
            
            # Contexto para el asistente de voz
            assistant_context = f"""Eres el Coach de Liderazgo de {contexto_usuario.get('nombre', 'el usuario')}, 
{contexto_usuario.get('cargo', 'manager')} en Grupo Orenes. 

Desafíos actuales: {contexto_usuario.get('desafios_equipo', 'gestión de equipo')}.

Ayúdalo a practicar conversaciones difíciles, dar feedback o resolver conflictos."""
            
            payload = {
                "phoneNumberId": telefono,
                "assistantId": "tu_assistant_id",  # Configurar en VAPI
                "metadata": {
                    "user_name": contexto_usuario.get('nombre'),
                    "cargo": contexto_usuario.get('cargo'),
                    "context": assistant_context
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.vapi.ai/call",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 201:
                    return {"success": True, "call": response.json()}
                else:
                    logger.error(f"Error VAPI: {response.status_code} - {response.text}")
                    return {"success": False, "error": "No se pudo iniciar la llamada"}
        
        except Exception as e:
            logger.error(f"Error iniciando llamada VAPI: {e}")
            return {"success": False, "error": str(e)}

# Instancia global
coach_ia = CoachIA()

# Funciones de conveniencia
async def consultar_coach(mensaje: str, contexto_usuario: dict) -> str:
    return await coach_ia.consultar_texto(mensaje, contexto_usuario)

async def llamar_coach(telefono: str, contexto_usuario: dict) -> dict:
    return await coach_ia.iniciar_llamada_vapi(telefono, contexto_usuario)
