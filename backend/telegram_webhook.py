"""
Telegram Webhook Handler para EvoLL
Maneja los mensajes entrantes de usuarios vía Telegram
"""

import os
import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_BOT_USERNAME = os.environ.get('TELEGRAM_BOT_USERNAME', 'Evoll_Orenes_Bot')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Esta será la referencia a la base de datos Supabase (se configura desde server.py)
supabase_db_instance = None

def set_database(db):
    """Configura la referencia a la base de datos Supabase"""
    global supabase_db_instance
    supabase_db_instance = db

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /start"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # Generar código de vinculación con el chat_id real
    codigo_vinculacion = f"EVOLL-{chat_id}"
    
    mensaje_bienvenida = f"""
🎯 **¡Bienvenido a EvoLL, {user.first_name}!**

Soy tu asistente de notificaciones para el Programa de Liderazgo Evolutivo de Grupo Orenes.

📱 **Para vincular tu cuenta:**
1. Ve a tu perfil en la plataforma EvoLL
2. En la sección "Telegram Bot", ingresa este código:

🔑 **Tu Código de Vinculación:**
`{codigo_vinculacion}`

Una vez vinculado, recibirás:
• 📬 3 notificaciones semanales (L-M-V)
• 💡 Preguntas de reflexión de liderazgo
• 📊 Recordatorios de evaluaciones mensuales

_¿Necesitas ayuda? Usa /ayuda_
    """
    
    await update.message.reply_text(
        mensaje_bienvenida,
        parse_mode='Markdown'
    )
    
    logger.info(f"Usuario {user.first_name} ({chat_id}) inició conversación")

async def ayuda_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /ayuda"""
    mensaje_ayuda = """
📖 **Comandos disponibles:**

/start - Iniciar bot y obtener código de vinculación
/ayuda - Mostrar esta ayuda
/estado - Ver estado de tu vinculación
/desactivar - Pausar notificaciones
/activar - Reactivar notificaciones

💬 **También puedes:**
- Responder directamente a las preguntas que te envío
- Enviarme consultas sobre el programa

_¿Problemas técnicos? Contacta con soporte en la plataforma._
    """
    
    await update.message.reply_text(mensaje_ayuda, parse_mode='Markdown')

async def estado_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para comando /estado"""
    chat_id = str(update.effective_chat.id)
    
    if not supabase_db_instance:
        await update.message.reply_text("⚠️ Error: Base de datos no disponible")
        return
    
    # Buscar usuario vinculado
    user = await supabase_db_instance.find_user_by_telegram_chat_id(chat_id)
    
    if user:
        nombre = user.get('nombre', 'Usuario')
        notif_activas = user.get('notificaciones_activas', True)
        estado_icon = "✅" if notif_activas else "⏸️"
        
        mensaje = f"""
{estado_icon} **Estado de tu cuenta:**

👤 Usuario: {nombre}
📱 Chat ID: `{chat_id}`
🔔 Notificaciones: {'Activas' if notif_activas else 'Pausadas'}

_Todo funcionando correctamente_
        """
    else:
        mensaje = f"""
⚠️ **Cuenta no vinculada**

Tu Telegram aún no está vinculado a tu cuenta EvoLL.

🔑 **Código de vinculación:**
`EVOLL-{chat_id}`

👉 Copia este código y pégalo en tu perfil de la plataforma EvoLL.
        """
    
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def desactivar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para desactivar notificaciones"""
    chat_id = str(update.effective_chat.id)
    
    if not supabase_db_instance:
        await update.message.reply_text("⚠️ Error: Base de datos no disponible")
        return
    
    # Buscar usuario por chat_id
    user = await supabase_db_instance.find_user_by_telegram_chat_id(chat_id)
    
    if user:
        await supabase_db_instance.update_user_notificaciones(user['id'], False)
        await update.message.reply_text(
            "⏸️ **Notificaciones pausadas**\n\n"
            "Ya no recibirás notificaciones automáticas.\n"
            "Usa /activar para reactivarlas."
        )
    else:
        await update.message.reply_text(
            "⚠️ No se pudo pausar las notificaciones. "
            "Asegúrate de que tu cuenta esté vinculada."
        )

async def activar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para activar notificaciones"""
    chat_id = str(update.effective_chat.id)
    
    if not supabase_db_instance:
        await update.message.reply_text("⚠️ Error: Base de datos no disponible")
        return
    
    # Buscar usuario por chat_id
    user = await supabase_db_instance.find_user_by_telegram_chat_id(chat_id)
    
    if user:
        await supabase_db_instance.update_user_notificaciones(user['id'], True)
        await update.message.reply_text(
            "✅ **Notificaciones activadas**\n\n"
            "Volverás a recibir las notificaciones del programa."
        )
    else:
        await update.message.reply_text(
            "⚠️ No se pudo activar las notificaciones. "
            "Asegúrate de que tu cuenta esté vinculada."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensajes de texto normales (respuestas del usuario)"""
    chat_id = str(update.effective_chat.id)
    texto = update.message.text
    
    if not supabase_db_instance:
        logger.error("Base de datos no disponible")
        return
    
    # Buscar usuario
    user = await supabase_db_instance.find_user_by_telegram_chat_id(chat_id)
    
    if not user:
        await update.message.reply_text(
            "⚠️ Tu cuenta no está vinculada aún.\n\n"
            f"Usa el código `EVOLL-{chat_id}` en tu perfil de la plataforma.",
            parse_mode='Markdown'
        )
        return
    
    # Buscar pregunta pendiente de respuesta para este usuario
    from datetime import datetime, timezone
    
    pregunta_pendiente = await supabase_db_instance.find_pending_respuesta_lmv(user['id'])
    
    if pregunta_pendiente:
        # ¡Hay una pregunta pendiente! Guardar respuesta
        await supabase_db_instance.update_respuesta_lmv_by_id(
            pregunta_pendiente['id'],
            {
                "respuesta": texto,
                "fecha_respuesta": datetime.now(timezone.utc).isoformat(),
                "enviado_via": "telegram",
                "puntos_otorgados": 10
            }
        )
        
        # Otorgar puntos al usuario
        await supabase_db_instance.increment_user_points(user['id'], 10)
        
        # Respuesta exitosa
        await update.message.reply_text(
            "✅ **¡Respuesta guardada!**\n\n"
            "Has ganado **+10 puntos** 🎉\n\n"
            "_Gracias por tu reflexión sobre liderazgo._",
            parse_mode='Markdown'
        )
        
        logger.info(f"✅ Respuesta L-M-V guardada: {user.get('nombre')} ({chat_id}) +10 pts")
    else:
        # No hay pregunta pendiente, guardar como mensaje general
        await supabase_db_instance.create_telegram_message({
            "user_id": user['id'],
            "chat_id": chat_id,
            "mensaje": texto,
            "fecha": update.message.date.isoformat(),
            "procesado": False
        })
        
        await update.message.reply_text(
            "📝 Mensaje recibido.\n\n"
            "Si quieres consultar al Coach IA o ver tus preguntas, "
            "entra a la plataforma web.\n\n"
            "_¿Necesitas ayuda? Usa /ayuda_",
            parse_mode='Markdown'
        )
        
        logger.info(f"Mensaje general recibido de {user.get('nombre')} ({chat_id})")


def create_telegram_app():
    """Crea y configura la aplicación de Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN no configurado")
        return None
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("ayuda", ayuda_command))
    application.add_handler(CommandHandler("estado", estado_command))
    application.add_handler(CommandHandler("desactivar", desactivar_command))
    application.add_handler(CommandHandler("activar", activar_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info(f"Bot de Telegram configurado: @{TELEGRAM_BOT_USERNAME}")
    
    return application

# Función para iniciar el bot en modo polling (para desarrollo/testing)
async def start_bot_polling():
    """Inicia el bot en modo polling para recibir mensajes"""
    application = create_telegram_app()
    if application:
        try:
            # Intentar limpiar cualquier instancia previa del bot
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                logger.info("Webhook limpiado para evitar conflictos")
            except Exception as e:
                logger.warning(f"No se pudo limpiar webhook: {e}")
            
            await application.initialize()
            await application.start()
            
            # Intentar iniciar polling con manejo de conflictos
            try:
                await application.updater.start_polling(
                    drop_pending_updates=True,
                    allowed_updates=Update.ALL_TYPES
                )
                logger.info("✅ Bot iniciado en modo polling correctamente")
                return application
            except Exception as e:
                if "Conflict" in str(e):
                    logger.error("❌ Conflicto: Ya hay otra instancia del bot corriendo")
                    logger.info("Intentando detener instancia previa...")
                    # Intentar detener y reintentar
                    await application.stop()
                    await application.shutdown()
                    return None
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"❌ Error iniciando bot de Telegram: {e}")
            return None
    return None

# Función para detener el bot
async def stop_bot_polling(application):
    """Detiene el bot"""
    if application:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("Bot detenido")
