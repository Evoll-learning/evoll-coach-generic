"""
Verificar que el schema de Supabase se creó correctamente
"""

import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

async def verificar_schema():
    """Verifica que todas las tablas existen y están listas"""
    
    print("\n" + "="*70)
    print("🔍 VERIFICANDO SCHEMA DE SUPABASE")
    print("="*70 + "\n")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    # Lista de tablas que deben existir
    tablas_esperadas = [
        'users',
        'respuestas_lmv',
        'conversaciones_coach',
        'telegram_messages',
        'badges',
        'user_badges',
        'actividades',
        'user_sessions'
    ]
    
    print("📊 Verificando tablas...\n")
    
    tablas_ok = []
    tablas_error = []
    
    for tabla in tablas_esperadas:
        try:
            # Intentar hacer un count en cada tabla
            result = supabase.table(tabla).select("*", count="exact").limit(0).execute()
            count = result.count if hasattr(result, 'count') else 0
            print(f"   ✅ {tabla:30s} - OK (registros: {count})")
            tablas_ok.append(tabla)
        except Exception as e:
            print(f"   ❌ {tabla:30s} - ERROR: {str(e)[:50]}")
            tablas_error.append(tabla)
    
    print("\n" + "-"*70)
    
    # Verificar badges (deben existir 6 badges iniciales)
    try:
        badges_result = supabase.table('badges').select("*").execute()
        num_badges = len(badges_result.data) if badges_result.data else 0
        print(f"\n🏅 Badges iniciales: {num_badges}/6")
        if num_badges == 6:
            print("   ✅ Todos los badges se crearon correctamente")
        else:
            print(f"   ⚠️  Faltan badges ({num_badges}/6)")
    except Exception as e:
        print(f"   ❌ Error verificando badges: {e}")
    
    # Resumen
    print("\n" + "="*70)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("="*70)
    print(f"\n✅ Tablas OK: {len(tablas_ok)}/{len(tablas_esperadas)}")
    print(f"❌ Tablas con error: {len(tablas_error)}/{len(tablas_esperadas)}")
    
    if len(tablas_error) == 0:
        print("\n🎉 ¡TODO PERFECTO! El schema está completamente configurado.")
        print("\n✅ Listo para migrar datos de MongoDB → Supabase")
        return True
    else:
        print("\n⚠️  Hay problemas con algunas tablas:")
        for tabla in tablas_error:
            print(f"   - {tabla}")
        return False

if __name__ == "__main__":
    resultado = asyncio.run(verificar_schema())
    
    if resultado:
        print("\n" + "="*70)
        print("🚀 SIGUIENTE PASO: Migración de datos")
        print("="*70)
        print("\nEjecuta:")
        print("   python migrate_mongodb_to_supabase.py")
        print("\n")
    else:
        print("\n⚠️  Revisa los errores antes de continuar")
