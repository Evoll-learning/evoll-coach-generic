"""
Migrar respuestas L-M-V de MongoDB a Supabase
"""

import os
import asyncio
from supabase import create_client, Client
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

async def migrar_respuestas():
    """Migra respuestas L-M-V de MongoDB a Supabase"""
    
    print("\n" + "="*70)
    print("🔄 MIGRANDO RESPUESTAS L-M-V")
    print("="*70 + "\n")
    
    # Conectar a MongoDB
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    mongo_db = mongo_client[DB_NAME]
    
    # Conectar a Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Obtener respuestas de MongoDB
    respuestas = await mongo_db.respuestas_lmv.find().to_list(length=None)
    
    print(f"📊 Respuestas en MongoDB: {len(respuestas)}")
    
    migradas = 0
    errores = 0
    
    for resp in respuestas:
        try:
            # Mapear tipos a los permitidos en Supabase
            tipo_original = resp.get('tipo', 'Liderazgo')
            if tipo_original in ['Reflexiva', 'Práctica', 'Aplicada']:
                tipo_mapeado = 'Liderazgo'  # Por defecto
            else:
                tipo_mapeado = tipo_original
            
            # Preparar datos para Supabase (adaptando nombres de columnas)
            data = {
                'id': resp.get('id'),
                'user_id': resp.get('user_id'),
                'semana': resp.get('semana'),
                'numero_envio': resp.get('numero_envio'),
                'tipo': tipo_mapeado,  # Usar tipo mapeado
                'competencia': resp.get('competencia'),
                'pregunta': resp.get('pregunta'),
                'respuesta': resp.get('respuesta_texto'),  # respuesta_texto -> respuesta
                'fecha_respuesta': resp.get('fecha_respuesta'),
                'feedback': resp.get('feedback_ia'),  # feedback_ia -> feedback
                'puntos_otorgados': resp.get('puntos_otorgados', 0),
                'enviado_via': 'web'
            }
            
            # Insertar en Supabase
            result = supabase.table('respuestas_lmv').upsert(data).execute()
            migradas += 1
            print(f"   ✅ Respuesta migrada: {resp.get('pregunta')[:50]}...")
            
        except Exception as e:
            errores += 1
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*70}")
    print(f"📊 RESUMEN:")
    print(f"   ✅ Migradas: {migradas}")
    print(f"   ❌ Errores: {errores}")
    print(f"{'='*70}\n")
    
    mongo_client.close()

if __name__ == "__main__":
    asyncio.run(migrar_respuestas())
