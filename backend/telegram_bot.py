"""
Bot de Telegram para notificaciones EvoLL
Envía notificaciones automáticas de preguntas L-M-V a los managers
"""

import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import logging

load_dotenv()

# Configuración
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN no configurado. Bot deshabilitado.")
            self.bot = None
        else:
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    async def enviar_notificacion_pregunta(self, chat_id: str, pregunta: dict, link: str):
        """
        Envía notificación de nueva pregunta L-M-V
        
        Args:
            chat_id: ID de chat de Telegram del usuario
            pregunta: Dict con datos de la pregunta
            link: URL a la plataforma
        """
        if not self.bot:
            logger.warning("Bot no configurado. No se puede enviar notificación.")
            return False
        
        mensaje = f"""
🎯 **¡Nueva pregunta EvoLL!**

📅 Semana {pregunta.get('semana', 'N/A')} • {pregunta.get('numero_envio', 'N/A')}
🏷️ Tipo: {pregunta.get('tipo', 'Reflexiva')}
💡 Competencia: {pregunta.get('competencia', 'Liderazgo')}

**Pregunta:**
{pregunta.get('pregunta', '')}

👉 [Responder ahora]({link})

_Tiempo estimado: 2-3 minutos_
        """.strip()
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=mensaje,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            logger.info(f"Notificación enviada a {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Error enviando notificación a {chat_id}: {e}")
            return False
    
    async def enviar_recordatorio(self, chat_id: str, mensaje: str):
        """
        Envía recordatorio personalizado
        """
        if not self.bot:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=mensaje,
                parse_mode='Markdown'
            )
            return True
        except TelegramError as e:
            logger.error(f"Error enviando recordatorio: {e}")
            return False
    
    async def verificar_bot(self):
        """
        Verifica que el bot esté funcionando
        """
        if not self.bot:
            return False
        
        try:
            me = await self.bot.get_me()
            logger.info(f"Bot conectado: @{me.username}")
            return True
        except TelegramError as e:
            logger.error(f"Error verificando bot: {e}")
            return False

# Instancia global del notifier
telegram_notifier = TelegramNotifier()

# Función para uso directo en el servidor
async def notificar_pregunta_dia(chat_id: str, pregunta: dict, link: str):
    """
    Wrapper para enviar notificación de pregunta del día
    """
    return await telegram_notifier.enviar_notificacion_pregunta(chat_id, pregunta, link)

# Test del bot
if __name__ == "__main__":
    async def test_bot():
        notifier = TelegramNotifier()
        
        # Verificar bot
        if await notifier.verificar_bot():
            print("✅ Bot de Telegram funcionando correctamente")
            
            # Test de notificación (comentar el chat_id de prueba)
            # await notifier.enviar_notificacion_pregunta(
            #     chat_id="TU_CHAT_ID_AQUI",
            #     pregunta={
            #         "semana": 1,
            #         "numero_envio": "P1",
            #         "tipo": "Reflexiva",
            #         "competencia": "Autoconocimiento",
            #         "pregunta": "¿Cuáles son tus valores fundamentales?"
            #     },
            #     link="https://coach-ai-9.preview.emergentagent.com/dashboard"
            # )
        else:
            print("❌ Error en configuración del bot")
    
    asyncio.run(test_bot())
