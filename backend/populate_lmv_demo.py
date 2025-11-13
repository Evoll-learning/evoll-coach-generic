"""
Script para poblar preguntas L-M-V CON RESPUESTAS DE EJEMPLO
Para demostración del MVP a RRHH
"""
import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase_client import supabase_db

load_dotenv()

async def populate_demo_responses():
    """Agrega preguntas L-M-V con respuestas de ejemplo para demo"""
    
    # Buscar usuario: julio@evoll.es
    print("🔍 Buscando usuario julio@evoll.es...")
    user = await supabase_db.find_user_by_email("julio@evoll.es")
    
    if not user:
        print("❌ Usuario julio@evoll.es no encontrado.")
        return
    
    user_id = user['id']
    print(f"✅ Usuario encontrado: {user['nombre']} {user['apellido']} (ID: {user_id})")
    
    # Limpiar respuestas existentes
    print("\n🧹 Limpiando respuestas anteriores...")
    existing = await supabase_db.find_respuestas_by_user(user_id)
    for resp in existing:
        try:
            supabase_db.client.table('respuestas_lmv').delete().eq('id', resp['id']).execute()
        except:
            pass
    
    print(f"✅ Limpiadas {len(existing)} respuestas anteriores")
    
    # Crear respuestas de ejemplo con contenido realista
    print("\n📝 Creando preguntas y respuestas de EJEMPLO para demo...")
    
    ejemplos = [
        # Semana 1 - Liderazgo
        {
            "tipo": "Liderazgo",
            "pregunta": "¿Cuáles son los 3 valores fundamentales que guían tus decisiones profesionales? Describe una situación reciente donde cada uno de estos valores influyó en tu forma de actuar.",
            "respuesta": "Mis tres valores fundamentales son: 1) Transparencia - Siempre comunico abiertamente con mi equipo sobre cambios y decisiones. 2) Responsabilidad - Asumo las consecuencias de mis decisiones sin buscar excusas. 3) Empatía - Escucho activamente las preocupaciones de mi equipo antes de tomar decisiones que les afecten.",
            "competencia": "Identificar valores personales",
            "semana": 1,
            "numero_envio": "P1",
            "puntos": 10
        },
        # Semana 1 - Management
        {
            "tipo": "Management",
            "pregunta": "Piensa en el líder que más admiras. ¿Qué características específicas posee que te gustaría desarrollar? ¿Cuáles ya posees?",
            "respuesta": "Admiro a mi anterior jefe por su capacidad de delegar sin microgestionar. Ya poseo la habilidad de comunicar claramente, pero me gustaría desarrollar más paciencia al dar feedback correctivo.",
            "competencia": "Modelado de liderazgo",
            "semana": 1,
            "numero_envio": "P2",
            "puntos": 10
        },
        # Semana 1 - Valores
        {
            "tipo": "Valores",
            "pregunta": "Describe tu 'mejor yo' en el trabajo: ese momento donde sentiste que estabas operando en tu máximo potencial. ¿Qué condiciones lo hicieron posible?",
            "respuesta": "Mi mejor versión aparece cuando lidero proyectos retadores con autonomía. Necesito confianza del equipo directivo y recursos adecuados para brillar.",
            "competencia": "Reconocimiento de fortalezas",
            "semana": 1,
            "numero_envio": "P3",
            "puntos": 10
        },
        # Semana 2 - Liderazgo
        {
            "tipo": "Liderazgo",
            "pregunta": "¿Qué máscaras o roles adoptas en tu entorno laboral que no son auténticamente tú? ¿Por qué crees que las mantienes?",
            "respuesta": "A veces finjo más seguridad de la que tengo para no preocupar al equipo. Creo que es importante, pero podría ser más auténtico compartiendo mis dudas ocasionalmente.",
            "competencia": "Autenticidad personal",
            "semana": 2,
            "numero_envio": "P1",
            "puntos": 10
        },
        # Semana 2 - Management
        {
            "tipo": "Management",
            "pregunta": "Completa: 'Si no tuviera miedo en mi trabajo, yo...' Desarrolla al menos 3 escenarios diferentes.",
            "respuesta": "Si no tuviera miedo: 1) Propondría cambios más radicales en procesos obsoletos. 2) Tendría conversaciones más directas sobre desempeño. 3) Delegaría más responsabilidades estratégicas.",
            "competencia": "Identificar limitaciones",
            "semana": 2,
            "numero_envio": "P2",
            "puntos": 10
        },
        # Semana 3 - Valores (SIN RESPONDER - para mostrar pregunta pendiente)
        {
            "tipo": "Valores",
            "pregunta": "Diseña tu 'declaración de liderazgo personal': ¿Qué tipo de líder quieres ser? ¿Qué legado quieres dejar?",
            "respuesta": None,
            "competencia": "Visión personal",
            "semana": 3,
            "numero_envio": "P3",
            "puntos": 0
        }
    ]
    
    agregadas = 0
    for i, ejemplo in enumerate(ejemplos, 1):
        try:
            # Crear fecha de respuesta realista (hace X días)
            dias_atras = len(ejemplos) - i
            fecha = datetime.now(timezone.utc) - timedelta(days=dias_atras)
            
            respuesta_data = {
                "user_id": user_id,
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
                agregadas += 1
                status = "✅ RESPONDIDA" if ejemplo["respuesta"] else "⏳ PENDIENTE"
                print(f"  {status}: Semana {ejemplo['semana']} - {ejemplo['tipo']} ({ejemplo['competencia']})")
            
        except Exception as e:
            print(f"  ❌ Error en ejemplo {i}: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Preguntas de DEMO creadas: {agregadas}/{len(ejemplos)}")
    print(f"{'='*60}")
    
    # Actualizar puntos del usuario
    total_puntos = sum(e["puntos"] for e in ejemplos if e["respuesta"])
    print(f"\n🎯 Actualizando puntos totales del usuario: +{total_puntos} puntos")
    
    try:
        await supabase_db.update_user(user_id, {"puntos_totales": total_puntos})
        print("✅ Puntos actualizados")
    except Exception as e:
        print(f"⚠️ No se pudieron actualizar puntos: {e}")
    
    # Verificar resultado final
    final_respuestas = await supabase_db.find_respuestas_by_user(user_id)
    print(f"\n📊 Total de respuestas para {user['nombre']}: {len(final_respuestas)}")
    
    respondidas = sum(1 for r in final_respuestas if r.get('respuesta'))
    pendientes = len(final_respuestas) - respondidas
    
    print(f"  ✅ Respondidas: {respondidas}")
    print(f"  ⏳ Pendientes: {pendientes}")
    
    print("\n🎉 ¡Demo data lista para mostrar a RRHH!")


if __name__ == "__main__":
    print("="*60)
    print("  POBLAR DEMO DATA L-M-V PARA MVP")
    print("="*60)
    print("\n⚠️  IMPORTANTE: Este script crea datos de EJEMPLO")
    print("   para demostración del MVP a RRHH de Orenes\n")
    
    asyncio.run(populate_demo_responses())
    
    print("\n✅ Script completado. Recarga el dashboard para ver los cambios.")
