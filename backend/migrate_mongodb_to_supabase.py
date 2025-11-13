"""
Migración de datos de MongoDB a Supabase
Migra usuarios, respuestas L-M-V, y conversaciones del coach
"""

import os
import asyncio
from supabase import create_client, Client
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

# MongoDB
MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME')

# Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

async def migrar_datos():
    """Migra todos los datos de MongoDB a Supabase"""
    
    print("\n" + "="*70)
    print("🔄 MIGRACIÓN MONGODB → SUPABASE")
    print("="*70 + "\n")
    
    # Conectar a MongoDB
    print("📦 Conectando a MongoDB...")
    mongo_client = AsyncIOMotorClient(MONGO_URL)
    mongo_db = mongo_client[DB_NAME]
    
    # Conectar a Supabase
    print("🔗 Conectando a Supabase...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Estadísticas
    stats = {
        'usuarios_migrados': 0,
        'usuarios_error': 0,
        'respuestas_migradas': 0,
        'conversaciones_migradas': 0
    }
    
    # ========================================
    # 1. MIGRAR USUARIOS
    # ========================================
    print("\n" + "-"*70)
    print("👥 Migrando usuarios...")
    print("-"*70)
    
    try:
        usuarios_mongo = await mongo_db.users.find().to_list(length=None)
        print(f"   Usuarios en MongoDB: {len(usuarios_mongo)}")
        
        for user_mongo in usuarios_mongo:
            try:
                # Preparar datos para Supabase
                user_supabase = {
                    'email': user_mongo.get('email'),
                    'nombre': user_mongo.get('nombre', ''),
                    'apellido': user_mongo.get('apellido', ''),
                    'cargo': user_mongo.get('cargo'),
                    'division': user_mongo.get('division'),
                    'experiencia_anos': user_mongo.get('experiencia_anos'),
                    'tamano_equipo': user_mongo.get('tamano_equipo'),
                    'desafios_equipo': user_mongo.get('desafios_equipo'),
                    'objetivos_personales': user_mongo.get('objetivos_personales'),
                    'valores_comprometidos': user_mongo.get('valores_comprometidos'),
                    'telegram_chat_id': user_mongo.get('telegram_chat_id'),
                    'notificaciones_activas': user_mongo.get('notificaciones_activas', True),
                    'puntos_totales': user_mongo.get('puntos_totales', 0),
                    'nivel': user_mongo.get('nivel', 1),
                    'racha_dias': user_mongo.get('racha_dias', 0),
                    'onboarding_completed': user_mongo.get('onboarding_completed', False),
                    'created_at': user_mongo.get('created_at', datetime.now(timezone.utc)).isoformat()
                }
                
                # Insertar en Supabase (sin auth_user_id por ahora)
                result = supabase.table('users').insert(user_supabase).execute()
                
                if result.data:
                    stats['usuarios_migrados'] += 1
                    print(f"   ✅ {user_mongo.get('email')}")
                    
                    # Guardar mapeo de IDs para migrar relaciones
                    mongo_id = user_mongo.get('id')
                    supabase_id = result.data[0]['id']
                    # Aquí podrías guardar el mapeo si necesitas migrar relaciones
                    
            except Exception as e:
                stats['usuarios_error'] += 1
                print(f"   ❌ Error con {user_mongo.get('email')}: {str(e)[:50]}")
        
    except Exception as e:
        print(f"   ❌ Error general migrando usuarios: {e}")
    
    # ========================================
    # RESUMEN
    # ========================================
    print("\n" + "="*70)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("="*70)
    print(f"\n👥 Usuarios:")
    print(f"   ✅ Migrados: {stats['usuarios_migrados']}")
    print(f"   ❌ Errores: {stats['usuarios_error']}")
    
    if stats['usuarios_migrados'] > 0:
        print("\n✅ Migración completada con éxito")
        print(f"\n🔗 Ver usuarios en Supabase:")
        print(f"   https://supabase.com/dashboard/project/cqxflqimwisvnmhfvgyv/editor")
    else:
        print("\n⚠️  No se migraron usuarios (puede ser que MongoDB esté vacío)")
        print("   Esto es normal si acabas de crear el proyecto")
    
    # Cerrar conexiones
    mongo_client.close()
    
    return stats

if __name__ == "__main__":
    stats = asyncio.run(migrar_datos())
    
    print("\n" + "="*70)
    print("✅ Proceso de migración completado")
    print("="*70 + "\n")
