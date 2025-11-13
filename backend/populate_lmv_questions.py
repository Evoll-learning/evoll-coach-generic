"""
Script para poblar preguntas L-M-V de ejemplo en Supabase
"""
import asyncio
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase_client import supabase_db
from preguntas_lmv_completas import PREGUNTAS_LMV_COMPLETAS

load_dotenv()

async def populate_sample_questions():
    """Agrega preguntas de ejemplo para demostración"""
    
    # Buscar usuario de prueba: julio@evoll.es
    print("🔍 Buscando usuario julio@evoll.es...")
    user = await supabase_db.find_user_by_email("julio@evoll.es")
    
    if not user:
        print("❌ Usuario julio@evoll.es no encontrado. Debes registrarte primero.")
        return
    
    user_id = user['id']
    print(f"✅ Usuario encontrado: {user['nombre']} {user['apellido']} (ID: {user_id})")
    
    # Verificar si ya tiene preguntas
    existing = await supabase_db.find_respuestas_by_user(user_id)
    if existing:
        print(f"⚠️ El usuario ya tiene {len(existing)} respuestas L-M-V en la base de datos.")
        confirm = input("¿Deseas agregar más preguntas de ejemplo? (s/n): ")
        if confirm.lower() != 's':
            print("❌ Operación cancelada.")
            return
    
    # Agregar preguntas de ejemplo de las primeras 3 semanas
    print("\n📝 Agregando preguntas de ejemplo...")
    
    preguntas_agregadas = 0
    errores = 0
    
    # Semana 1: Liderazgo, Management, Valores
    for semana in [1, 2, 3]:
        week_data = PREGUNTAS_LMV_COMPLETAS.get(semana, {})
        
        # P1, P2, P3 para cada semana
        for pregunta_num, pregunta_key in enumerate(["P1", "P2", "P3"], 1):
            pregunta_info = week_data.get(pregunta_key)
            
            if not pregunta_info:
                continue
            
            # Determinar tipo L-M-V basado en el número de pregunta
            if pregunta_num == 1:
                tipo = "Liderazgo"
            elif pregunta_num == 2:
                tipo = "Management"
            else:
                tipo = "Valores"
            
            # Datos de la pregunta
            respuesta_data = {
                "user_id": user_id,
                "semana": semana,
                "numero_envio": pregunta_key,
                "tipo": tipo,
                "competencia": pregunta_info.get("competencia", ""),
                "pregunta": pregunta_info.get("pregunta", ""),
                "respuesta": None,  # Sin responder
                "fecha_respuesta": None,
                "evaluado": False,
                "puntos_otorgados": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "enviado_via": "web"
            }
            
            try:
                result = await supabase_db.create_respuesta_lmv(respuesta_data)
                if result:
                    preguntas_agregadas += 1
                    print(f"  ✅ Semana {semana} - {tipo} ({pregunta_info['competencia']})")
                else:
                    errores += 1
                    print(f"  ❌ Error agregando Semana {semana} - {tipo}")
            except Exception as e:
                errores += 1
                print(f"  ❌ Excepción en Semana {semana} - {tipo}: {e}")
    
    print(f"\n{'='*50}")
    print(f"✅ Preguntas agregadas exitosamente: {preguntas_agregadas}")
    if errores > 0:
        print(f"❌ Errores: {errores}")
    print(f"{'='*50}")
    
    # Verificar resultado
    final_respuestas = await supabase_db.find_respuestas_by_user(user_id)
    print(f"\n📊 Total de preguntas L-M-V para {user['nombre']}: {len(final_respuestas)}")
    
    # Mostrar resumen por tipo
    liderazgo = sum(1 for r in final_respuestas if r.get('tipo') == 'Liderazgo')
    management = sum(1 for r in final_respuestas if r.get('tipo') == 'Management')
    valores = sum(1 for r in final_respuestas if r.get('tipo') == 'Valores')
    
    print(f"  - Liderazgo: {liderazgo}")
    print(f"  - Management: {management}")
    print(f"  - Valores: {valores}")


if __name__ == "__main__":
    print("="*50)
    print("  POBLAR PREGUNTAS L-M-V EN SUPABASE")
    print("="*50)
    
    asyncio.run(populate_sample_questions())
    
    print("\n✅ Script completado.")
