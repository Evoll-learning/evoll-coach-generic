"""
Script para inicializar el schema de Supabase
REQUIERE: Ejecutar SQL manualmente en dashboard
"""

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
PROJECT_ID = "cqxflqimwisvnmhfvgyv"

print("\n" + "="*70)
print("📊 CONFIGURACIÓN DEL SCHEMA DE SUPABASE")
print("="*70)

print(f"\n📍 Proyecto: {PROJECT_ID}")
print(f"🔗 URL: {SUPABASE_URL}\n")

print("📋 PASOS PARA CONFIGURAR:")
print("-" * 70)
print("\n1️⃣  Ve al SQL Editor de Supabase:")
print(f"   https://supabase.com/dashboard/project/{PROJECT_ID}/sql/new")

print("\n2️⃣  Copia el archivo SQL:")
print("   El archivo 'supabase_schema.sql' contiene todo el schema")

print("\n3️⃣  Pega y ejecuta:")
print("   - Pega todo el contenido en el editor")
print("   - Click en 'RUN' (botón verde abajo)")
print("   - Espera a que termine (verás 'Success')")

print("\n4️⃣  Verifica:")
print("   - Ve a 'Table Editor' en el menú lateral")
print("   - Deberías ver las tablas: users, respuestas_lmv, etc.")

print("\n5️⃣  Continúa:")
print("   - Una vez hecho, avísame")
print("   - Continuaré con la migración de datos")

print("\n" + "="*70)
print("✅ Cuando termines, escribe: 'SQL ejecutado' o 'listo'")
print("="*70 + "\n")
