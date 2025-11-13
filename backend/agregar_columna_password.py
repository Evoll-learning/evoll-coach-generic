"""
Script para agregar columna hashed_password a la tabla users en Supabase
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

print("🔧 Intentando agregar columna hashed_password...")
print("NOTA: Esto debe hacerse desde el SQL Editor de Supabase")
print("\n" + "="*70)
print("EJECUTA ESTE SQL EN SUPABASE:")
print("="*70)
print("""
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS hashed_password TEXT;
""")
print("="*70)
print("\n1. Ve a: https://supabase.com/dashboard")
print("2. Selecciona tu proyecto")
print("3. Ve a 'SQL Editor'")
print("4. Copia y pega el SQL de arriba")
print("5. Click 'Run'")
print("\nDespués de ejecutar el SQL, vuelve aquí y presiona Enter...")

input()

print("\n✅ Continuando...")
print("Verificando que la columna exista...")

try:
    # Intentar hacer una consulta que use la columna
    result = supabase.table('users').select('email, hashed_password').limit(1).execute()
    print("✅ Columna hashed_password existe!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nAsegúrate de haber ejecutado el SQL en Supabase")
