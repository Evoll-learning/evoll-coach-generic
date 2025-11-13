"""
Script para ejecutar como cron job
Ejecutar diariamente a las 9:00 AM para enviar preguntas L-M-V
"""

import asyncio
import httpx
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL del backend (local)
BACKEND_URL = "http://localhost:8001/api"

async def ejecutar_cron():
    """Ejecuta el endpoint de envío de preguntas"""
    
    logger.info("=" * 60)
    logger.info(f"CRON JOB INICIADO - {datetime.now()}")
    logger.info("=" * 60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(f"{BACKEND_URL}/cron/enviar-pregunta-dia")
            response.raise_for_status()
            
            resultado = response.json()
            
            logger.info(f"✅ Cron ejecutado exitosamente")
            logger.info(f"   Tipo: {resultado.get('tipo', 'N/A')}")
            logger.info(f"   Enviados: {resultado.get('usuarios_enviados', 0)}")
            logger.info(f"   Errores: {resultado.get('errores', 0)}")
            
            if resultado.get('errores_detalle'):
                logger.warning(f"   Errores detalle: {resultado['errores_detalle']}")
            
            return True
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Error HTTP: {e.response.status_code}")
            logger.error(f"   Respuesta: {e.response.text}")
            return False
            
        except httpx.RequestError as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            return False
        
        finally:
            logger.info("=" * 60)
            logger.info("CRON JOB FINALIZADO")
            logger.info("=" * 60)

if __name__ == "__main__":
    resultado = asyncio.run(ejecutar_cron())
    exit(0 if resultado else 1)
