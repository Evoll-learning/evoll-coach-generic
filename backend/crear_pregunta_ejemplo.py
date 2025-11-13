"""
Script para crear una pregunta L-M-V de ejemplo para todos los usuarios
Esto ayuda a que vean cómo funciona el sistema antes de activar el cron
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'evoll_db')

async def crear_pregunta_ejemplo():
    """Crea una pregunta de ejemplo para todos los usuarios"""
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Creando pregunta L-M-V de ejemplo...")
    
    # Obtener todos los usuarios
    usuarios = await db.users.find().to_list(length=None)
    
    if not usuarios:
        print("⚠️ No hay usuarios en el sistema")
        return
    
    print(f"📊 Encontrados {len(usuarios)} usuarios")
    
    # Pregunta de ejemplo
    pregunta_ejemplo = {
        "semana": 1,
        "bloque": 1,
        "numero_envio": "P1",
        "tipo": "Reflexiva",
        "competencia": "Comunicación",
        "pregunta": "¿Cuál es tu mayor fortaleza como líder y cómo la demuestras a diario en tu equipo?"
    }
    
    creadas = 0
    
    for user in usuarios:
        try:
            # Verificar si ya tiene una respuesta de ejemplo
            existe = await db.respuestas_lmv.find_one({
                "user_id": user['id'],
                "numero_envio": "P1",
                "semana": 1
            })
            
            if existe:
                print(f"⏭️  {user['email']} ya tiene pregunta de ejemplo")
                continue
            
            # Crear respuesta pendiente (sin responder aún)
            respuesta_doc = {
                "id": str(uuid.uuid4()),
                "user_id": user['id'],
                "semana": pregunta_ejemplo['semana'],
                "bloque": pregunta_ejemplo['bloque'],
                "numero_envio": pregunta_ejemplo['numero_envio'],
                "tipo": pregunta_ejemplo['tipo'],
                "competencia": pregunta_ejemplo['competencia'],
                "pregunta": pregunta_ejemplo['pregunta'],
                "respuesta_texto": None,  # Pendiente de responder
                "respuesta_audio_url": None,
                "feedback_ia": None,
                "puntuacion": None,
                "fecha_envio": datetime.now(timezone.utc).isoformat(),
                "fecha_respuesta": None,
                "puntos_otorgados": 0
            }
            
            await db.respuestas_lmv.insert_one(respuesta_doc)
            creadas += 1
            print(f"✅ Pregunta creada para {user['email']}")
            
        except Exception as e:
            print(f"❌ Error con {user['email']}: {e}")
    
    print(f"\n🎉 Proceso completado!")
    print(f"   - Total usuarios: {len(usuarios)}")
    print(f"   - Preguntas creadas: {creadas}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(crear_pregunta_ejemplo())
