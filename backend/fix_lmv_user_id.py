"""
Script para verificar user_id y poblar preguntas correctamente
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase_client import supabase_db
from datetime import datetime, timezone, timedelta

load_dotenv()

async def fix_lmv_data():
    """Verificar user_id y poblar preguntas correctamente"""
    
    # Buscar usuario por email
    print("🔍 Buscando usuario julio@evoll.es...")
    user = await supabase_db.find_user_by_email("julio@evoll.es")
    
    if not user:
        print("❌ Usuario no encontrado")
        return
    
    user_id = user['id']
    print(f"✅ Usuario encontrado:")
    print(f"   ID: {user_id}")
    print(f"   Email: {user['email']}")
    print(f"   Nombre: {user['nombre']} {user['apellido']}")
    print(f"   Onboarding: {user.get('onboarding_completed', False)}")
    
    # Verificar respuestas existentes
    print(f"\n🔍 Buscando respuestas L-M-V para user_id: {user_id}...")
    respuestas = await supabase_db.find_respuestas_by_user(user_id)
    print(f"   Respuestas encontradas: {len(respuestas)}")
    
    if len(respuestas) > 0:
        print("\n🧹 Limpiando respuestas anteriores...")
        for resp in respuestas:
            try:
                supabase_db.client.table('respuestas_lmv').delete().eq('id', resp['id']).execute()
            except Exception as e:
                print(f"   Error eliminando {resp['id']}: {e}")
        print(f"   ✅ Limpiadas {len(respuestas)} respuestas")
    
    # Crear preguntas de ejemplo
    print(f"\n📝 Insertando preguntas de EJEMPLO para user_id: {user_id}...")
    
    ejemplos = [
        {
            "tipo": "Liderazgo",
            "pregunta": "¿Cuáles son los 3 valores fundamentales que guían tus decisiones profesionales?",
            "respuesta": "Mis tres valores fundamentales son: 1) Transparencia - Siempre comunico abiertamente con mi equipo. 2) Responsabilidad - Asumo las consecuencias de mis decisiones. 3) Empatía - Escucho activamente antes de decidir.",
            "competencia": "Identificar valores personales",
            "semana": 1,
            "numero_envio": "P1",
            "puntos": 10
        },
        {
            "tipo": "Management",
            "pregunta": "Piensa en el líder que más admiras. ¿Qué características posee que te gustaría desarrollar?",
            "respuesta": "Admiro la capacidad de delegar sin microgestionar. Ya poseo buena comunicación, pero quiero desarrollar más paciencia al dar feedback.",
            "competencia": "Modelado de liderazgo",
            "semana": 1,
            "numero_envio": "P2",
            "puntos": 10
        },
        {
            "tipo": "Valores",
            "pregunta": "Describe tu 'mejor yo' en el trabajo: ese momento donde sentiste que estabas en tu máximo potencial.",
            "respuesta": "Mi mejor versión aparece liderando proyectos retadores con autonomía. Necesito confianza del equipo directivo y recursos adecuados para brillar.",
            "competencia": "Reconocimiento de fortalezas",
            "semana": 1,
            "numero_envio": "P3",
            "puntos": 10
        },
        {
            "tipo": "Liderazgo",
            "pregunta": "¿Qué máscaras o roles adoptas en tu entorno laboral que no son auténticamente tú?",
            "respuesta": "A veces finjo más seguridad de la que tengo para no preocupar al equipo. Podría ser más auténtico compartiendo mis dudas ocasionalmente.",
            "competencia": "Autenticidad personal",
            "semana": 2,
            "numero_envio": "P1",
            "puntos": 10
        },
        {
            "tipo": "Management",
            "pregunta": "Completa: 'Si no tuviera miedo en mi trabajo, yo...' Desarrolla al menos 3 escenarios.",
            "respuesta": "Si no tuviera miedo: 1) Propondría cambios más radicales en procesos obsoletos. 2) Tendría conversaciones más directas sobre desempeño. 3) Delegaría más responsabilidades estratégicas.",
            "competencia": "Identificar limitaciones",
            "semana": 2,
            "numero_envio": "P2",
            "puntos": 10
        },
        {
            "tipo": "Valores",
            "pregunta": "Diseña tu 'declaración de liderazgo personal': ¿Qué tipo de líder quieres ser?",
            "respuesta": None,  # PENDIENTE
            "competencia": "Visión personal",
            "semana": 3,
            "numero_envio": "P3",
            "puntos": 0
        }
    ]
    
    insertadas = 0
    for i, ejemplo in enumerate(ejemplos, 1):
        try:
            dias_atras = len(ejemplos) - i
            fecha = datetime.now(timezone.utc) - timedelta(days=dias_atras)
            
            # IMPORTANTE: Usar el user_id correcto
            respuesta_data = {
                "user_id": user_id,  # ← Aquí está la clave
                "semana": ejemplo["semana"],
                "numero_envio": ejemplo["numero_envio"],
                "tipo": ejemplo["tipo"],
                "competencia": ejemplo["competencia"],
                "pregunta": ejemplo["pregunta"],
                "respuesta": ejemplo["respuesta"],
                "fecha_respuesta": fecha.isoformat() if ejemplo["respuesta"] else None,
                "evaluado": False,
                "puntos_otorgados": ejemplo["puntos"],
                "created_at": (fecha - timedelta(days=1)).isoformat(),
                "enviado_via": "web"
            }
            
            result = await supabase_db.create_respuesta_lmv(respuesta_data)
            if result:
                insertadas += 1
                status = "✅" if ejemplo["respuesta"] else "⏳"
                print(f"   {status} Semana {ejemplo['semana']} - {ejemplo['tipo']}")
        except Exception as e:
            print(f"   ❌ Error en ejemplo {i}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Insertadas {insertadas}/{len(ejemplos)} preguntas")
    print(f"{'='*60}")
    
    # Actualizar puntos
    total_puntos = sum(e["puntos"] for e in ejemplos if e["respuesta"])
    await supabase_db.update_user(user_id, {"puntos_totales": total_puntos})
    print(f"\n🎯 Puntos actualizados: {total_puntos}")
    
    # Verificar
    respuestas_final = await supabase_db.find_respuestas_by_user(user_id)
    print(f"\n📊 VERIFICACIÓN FINAL:")
    print(f"   User ID: {user_id}")
    print(f"   Total respuestas: {len(respuestas_final)}")
    print(f"   Respondidas: {sum(1 for r in respuestas_final if r.get('respuesta'))}")
    print(f"   Pendientes: {sum(1 for r in respuestas_final if not r.get('respuesta'))}")
    
    print("\n✅ ¡Listo! Recarga el dashboard para ver las preguntas.")

if __name__ == "__main__":
    print("="*60)
    print("  FIX L-M-V DATA - USER ID CORRECTO")
    print("="*60)
    asyncio.run(fix_lmv_data())
