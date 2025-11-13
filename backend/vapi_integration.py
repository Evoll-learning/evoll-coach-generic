"""
Integración con VAPI para llamadas de voz con el Coach IA
"""

import os
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.environ.get('VAPI_API_KEY')
VAPI_BASE_URL = "https://api.vapi.ai"

logger = logging.getLogger(__name__)

async def iniciar_llamada_vapi(phone_number: str, user_context: dict, assistant_id: str = None):
    """
    Inicia una llamada de voz con VAPI
    
    Args:
        phone_number: Número de teléfono del usuario (formato internacional: +34612345678)
        user_context: Contexto del usuario (nombre, cargo, división, etc)
        assistant_id: ID del assistant de VAPI (opcional, se usa env var si no se proporciona)
    
    Returns:
        dict con call_id, status y detalles de la llamada
    """
    
    if not VAPI_API_KEY:
        raise Exception("VAPI_API_KEY no está configurado en .env")
    
    # Usar assistant_id de parámetro o de variable de entorno
    asst_id = assistant_id or os.environ.get('VAPI_ASSISTANT_ID')
    
    if not asst_id:
        raise Exception("VAPI_ASSISTANT_ID no está configurado. Configura el assistant primero en dashboard.vapi.ai")
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construir contexto personalizado para el assistant
    user_info = f"""
Usuario: {user_context.get('nombre', 'Usuario')} {user_context.get('apellido', '')}
Cargo: {user_context.get('cargo', 'No especificado')}
División: {user_context.get('division', 'No especificada')}
Años de experiencia: {user_context.get('experiencia_anos', 'N/A')}
Tamaño de equipo: {user_context.get('tamano_equipo', 'N/A')} personas
Objetivos: {user_context.get('objetivos_personales', 'No especificados')}
    """.strip()
    
    payload = {
        "assistant": {
            "assistantId": asst_id,
            # Podemos sobrescribir el system prompt con contexto del usuario
            "variableValues": {
                "user_context": user_info
            }
        },
        "phoneNumberId": None,  # VAPI usará su número por defecto
        "customer": {
            "number": phone_number,
            "name": f"{user_context.get('nombre', '')} {user_context.get('apellido', '')}".strip()
        }
    }
    
    logger.info(f"Iniciando llamada VAPI a {phone_number}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{VAPI_BASE_URL}/call/phone",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"✅ Llamada VAPI iniciada: {data.get('id')}")
            
            return {
                "success": True,
                "call_id": data.get('id'),
                "status": data.get('status'),
                "phone_number": phone_number,
                "assistant_id": asst_id
            }
            
        except httpx.HTTPStatusError as e:
            error_msg = f"Error HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"❌ VAPI Error: {error_msg}")
            raise Exception(error_msg)
            
        except httpx.RequestError as e:
            error_msg = f"Error de conexión con VAPI: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)


async def obtener_estado_llamada(call_id: str):
    """
    Obtiene el estado de una llamada en curso
    
    Args:
        call_id: ID de la llamada
        
    Returns:
        dict con información del estado de la llamada
    """
    
    if not VAPI_API_KEY:
        raise Exception("VAPI_API_KEY no está configurado")
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{VAPI_BASE_URL}/call/{call_id}",
                headers=headers
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "call_id": call_id,
                "status": data.get('status'),
                "duration": data.get('duration'),
                "cost": data.get('cost'),
                "transcript": data.get('transcript')
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de llamada: {e}")
            raise Exception(str(e))


async def verificar_configuracion_vapi():
    """
    Verifica que VAPI está correctamente configurado
    
    Returns:
        dict con información de la configuración
    """
    
    configurado = bool(VAPI_API_KEY)
    assistant_id = os.environ.get('VAPI_ASSISTANT_ID')
    
    return {
        "configurado": configurado,
        "api_key_presente": configurado,
        "assistant_id_presente": bool(assistant_id),
        "assistant_id": assistant_id if assistant_id else None,
        "mensaje": "Configuración completa" if (configurado and assistant_id) else "Falta configurar assistant_id"
    }


async def obtener_web_token(user_context: dict):
    """
    Genera un token temporal para el Web SDK de VAPI
    
    Args:
        user_context: Contexto del usuario (nombre, cargo, etc)
    
    Returns:
        dict con assistant_id y configuración para el Web SDK
    """
    
    assistant_id = os.environ.get('VAPI_ASSISTANT_ID')
    
    if not assistant_id:
        raise Exception("VAPI_ASSISTANT_ID no está configurado")
    
    # Para el Web SDK, simplemente devolvemos el assistant ID
    # El frontend lo usará directamente con VAPI Web SDK
    return {
        "assistant_id": assistant_id,
        "user_name": user_context.get('nombre', 'Usuario'),
        "user_cargo": user_context.get('cargo', 'No especificado'),
        "metadata": {
            "platform": "EvoLL Liderazgo",
            "division": user_context.get('division', 'N/A')
        }
    }
