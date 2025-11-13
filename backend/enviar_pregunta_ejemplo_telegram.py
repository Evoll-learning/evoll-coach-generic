"""
Script para enviar notificación de la pregunta de ejemplo por Telegram
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from telegram_bot import notificar_pregunta_dia

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'evoll_db')

async def enviar_notificacion_ejemplo():
    """Envía notificación de Telegram con la pregunta de ejemplo"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Enviando notificación de pregunta de ejemplo por Telegram...")
    
    # Obtener usuarios con Telegram vinculado
    usuarios = await db.users.find({
        "telegram_chat_id": {"$ne": None, "$exists": True}
    }).to_list(length=None)
    
    if not usuarios:
        print("⚠️ No hay usuarios con Telegram vinculado")
        return
    
    print(f"📊 Encontrados {len(usuarios)} usuarios con Telegram")
    
    # Pregunta de ejemplo
    pregunta = {
        "semana": 1,
        "numero_envio": "P1",
        "tipo": "Reflexiva",
        "competencia": "Comunicación",
        "pregunta": "¿Cuál es tu mayor fortaleza como líder y cómo la demuestras a diario en tu equipo?"
    }
    
    link = "https://coach-ai-9.preview.emergentagent.com/dashboard"
    
    enviadas = 0
    errores = 0
    
    for user in usuarios:
        try:
            chat_id = user['telegram_chat_id']
            print(f"📤 Enviando a {user['email']} (chat_id: {chat_id})...")
            
            resultado = await notificar_pregunta_dia(chat_id, pregunta, link)
            
            if resultado:
                enviadas += 1
                print(f"   ✅ Enviado")
            else:
                errores += 1
                print(f"   ❌ Error al enviar")
                
        except Exception as e:
            errores += 1
            print(f"   ❌ Excepción: {e}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   - Total usuarios con Telegram: {len(usuarios)}")
    print(f"   - Notificaciones enviadas: {enviadas}")
    print(f"   - Errores: {errores}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(enviar_notificacion_ejemplo())
