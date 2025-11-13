"""
Proxy para OpenAI Realtime API
Maneja la autenticación y conexión WebSocket desde el backend
"""

import asyncio
import websockets
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get('EMERGENT_LLM_KEY')
OPENAI_REALTIME_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"

async def proxy_websocket(client_ws):
    """
    Proxy entre el cliente (navegador) y OpenAI Realtime API
    """
    
    if not OPENAI_API_KEY:
        logger.error("EMERGENT_LLM_KEY no está configurada")
        await client_ws.send(json.dumps({
            "type": "error",
            "error": {"message": "API key no configurada"}
        }))
        return
    
    try:
        # Conectar a OpenAI con headers de autenticación
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1",
        }
        
        async with websockets.connect(OPENAI_REALTIME_URL, extra_headers=headers) as openai_ws:
            logger.info("✅ Conectado a OpenAI Realtime API")
            
            # Configurar sesión inicial
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": """Eres un coach ejecutivo experto en liderazgo del Grupo Orenes.

Tu metodología:
- Usa PREGUNTAS PODEROSAS para que el líder descubra sus propias soluciones
- Sé empático pero directo
- Tutea, español de España, natural y conversacional
- Máximo 60-80 palabras por intervención
- Escucha activamente y valida emociones

Áreas de expertise:
- Feedback bidireccional (hacia equipo y superiores)
- Comunicación y gestión de conflictos
- Inteligencia emocional aplicada
- Toma de decisiones estratégicas

Valores de Orenes:
- 56 años de experiencia
- Confianza y transparencia
- Compromiso con las personas
- Sentimiento familiar

Cierra siempre con UNA pregunta de compromiso sobre el siguiente paso concreto.""",
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "input_audio_transcription": {
                        "model": "whisper-1",
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500,
                    },
                    "temperature": 0.8,
                }
            }
            
            await openai_ws.send(json.dumps(session_config))
            
            # Crear tareas para bidireccional forwarding
            async def forward_to_openai():
                """Reenviar mensajes del cliente a OpenAI"""
                try:
                    async for message in client_ws:
                        await openai_ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    logger.info("Cliente desconectado")
            
            async def forward_to_client():
                """Reenviar mensajes de OpenAI al cliente"""
                try:
                    async for message in openai_ws:
                        await client_ws.send(message)
                except websockets.exceptions.ConnectionClosed:
                    logger.info("OpenAI desconectado")
            
            # Ejecutar ambas tareas concurrentemente
            await asyncio.gather(
                forward_to_openai(),
                forward_to_client(),
                return_exceptions=True
            )
            
    except Exception as e:
        logger.error(f"Error en proxy: {e}")
        try:
            await client_ws.send(json.dumps({
                "type": "error",
                "error": {"message": str(e)}
            }))
        except:
            pass
