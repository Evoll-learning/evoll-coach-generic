"""
Sistema de Gamificación - Puntos, Badges y Leaderboard
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import logging
import uuid

logger = logging.getLogger(__name__)

# Configuración de puntos
PUNTOS_CONFIG = {
    "respuesta_lmv": 10,
    "coach_consulta_texto": 5,
    "coach_consulta_audio": 7,
    "coach_llamada_vapi": 15,
    "racha_7_dias": 50,
    "racha_30_dias": 200,
    "login_diario": 2
}

async def otorgar_puntos(db: AsyncIOMotorDatabase, user_id: str, puntos: int, tipo: str, descripcion: str):
    """
    Otorga puntos a un usuario y registra la actividad
    
    Args:
        db: Database instance
        user_id: ID del usuario
        puntos: Cantidad de puntos a otorgar
        tipo: Tipo de actividad
        descripcion: Descripción de la actividad
        
    Returns:
        dict con información de los puntos otorgados y nivel
    """
    
    try:
        # Actualizar puntos del usuario
        result = await db.users.update_one(
            {"id": user_id},
            {
                "$inc": {"puntos_totales": puntos},
                "$set": {"ultima_actividad": datetime.now(timezone.utc)}
            }
        )
        
        if result.modified_count > 0:
            # Registrar actividad
            await db.actividades.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "tipo": tipo,
                "descripcion": descripcion,
                "puntos_ganados": puntos,
                "fecha": datetime.now(timezone.utc)
            })
            
            # Obtener usuario actualizado
            user = await db.users.find_one({"id": user_id})
            puntos_totales = user.get('puntos_totales', 0)
            nivel_actual = user.get('nivel', 1)
            
            # Lógica de niveles: cada 100 puntos = 1 nivel
            nuevo_nivel = (puntos_totales // 100) + 1
            
            subio_nivel = False
            if nuevo_nivel > nivel_actual:
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"nivel": nuevo_nivel}}
                )
                logger.info(f"🎉 Usuario {user_id} subió a nivel {nuevo_nivel}")
                subio_nivel = True
            
            # Verificar y otorgar badges
            badges_nuevos = await verificar_y_otorgar_badges(db, user_id, puntos_totales, user)
            
            logger.info(f"✅ Puntos otorgados: +{puntos} a {user_id} por {tipo} (Total: {puntos_totales})")
            
            return {
                "success": True,
                "puntos_otorgados": puntos,
                "puntos_totales": puntos_totales,
                "nivel_actual": nuevo_nivel,
                "subio_nivel": subio_nivel,
                "badges_nuevos": badges_nuevos
            }
        
        return {
            "success": False,
            "message": "No se pudo actualizar el usuario"
        }
        
    except Exception as e:
        logger.error(f"❌ Error otorgando puntos: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def verificar_y_otorgar_badges(db: AsyncIOMotorDatabase, user_id: str, puntos_totales: int, user: dict):
    """
    Verifica criterios de badges y otorga los que apliquen
    
    Returns:
        list de badges recién otorgados
    """
    
    badges_nuevos = []
    
    try:
        # Obtener badges que el usuario YA tiene
        user_badges = await db.user_badges.find({"user_id": user_id}).to_list(length=None)
        badges_ids_obtenidos = [ub.get('badge_id') for ub in user_badges]
        
        # Obtener todos los badges disponibles
        all_badges = await db.badges.find().to_list(length=None)
        
        for badge in all_badges:
            badge_id = badge.get('id')
            
            # Si ya lo tiene, skip
            if badge_id in badges_ids_obtenidos:
                continue
            
            # Verificar criterio según el código del badge
            codigo = badge.get('codigo')
            debe_otorgar = False
            
            if codigo == 'primer_paso':
                # Se otorga al completar onboarding
                debe_otorgar = user.get('onboarding_completed', False)
                
            elif codigo == 'reflexivo':
                # 10 respuestas L-M-V
                count = await db.respuestas_lmv.count_documents({"user_id": user_id, "respuesta": {"$ne": None}})
                debe_otorgar = count >= 10
                
            elif codigo == 'constante':
                # Racha de 7 días
                racha = user.get('racha_dias', 0)
                debe_otorgar = racha >= 7
                
            elif codigo == 'comunicador':
                # 20 consultas al coach
                count = await db.conversaciones_coach.count_documents({"user_id": user_id, "role": "user"})
                debe_otorgar = count >= 20
                
            elif codigo == 'maestro':
                # Completar todos los módulos (simplificado: 1000 puntos)
                debe_otorgar = puntos_totales >= 1000
                
            elif codigo == 'inspirador':
                # 5000 puntos
                debe_otorgar = puntos_totales >= 5000
            
            # Si cumple el criterio, otorgar badge
            if debe_otorgar:
                await db.user_badges.insert_one({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "badge_id": badge_id,
                    "obtenido_en": datetime.now(timezone.utc)
                })
                
                badges_nuevos.append({
                    "nombre": badge.get('nombre'),
                    "descripcion": badge.get('descripcion'),
                    "icono": badge.get('icono')
                })
                
                logger.info(f"🏅 Badge '{badge.get('nombre')}' otorgado a {user_id}")
        
        return badges_nuevos
        
    except Exception as e:
        logger.error(f"Error verificando badges: {e}")
        return []


async def obtener_leaderboard(db: AsyncIOMotorDatabase, limit: int = 10):
    """
    Obtiene el leaderboard de usuarios
    
    Returns:
        list de usuarios ordenados por puntos
    """
    
    try:
        # Obtener top usuarios por puntos
        usuarios = await db.users.find(
            {},
            {
                "id": 1,
                "nombre": 1,
                "apellido": 1,
                "puntos_totales": 1,
                "nivel": 1,
                "racha_dias": 1
            }
        ).sort("puntos_totales", -1).limit(limit).to_list(length=None)
        
        # Agregar badges de cada usuario
        leaderboard = []
        for idx, user in enumerate(usuarios, 1):
            # Contar badges
            badges_count = await db.user_badges.count_documents({"user_id": user['id']})
            
            leaderboard.append({
                "ranking": idx,
                "nombre": user.get('nombre', ''),
                "apellido": user.get('apellido', ''),
                "puntos_totales": user.get('puntos_totales', 0),
                "nivel": user.get('nivel', 1),
                "racha_dias": user.get('racha_dias', 0),
                "total_badges": badges_count
            })
        
        return leaderboard
        
    except Exception as e:
        logger.error(f"Error obteniendo leaderboard: {e}")
        return []


async def obtener_badges_usuario(db: AsyncIOMotorDatabase, user_id: str):
    """
    Obtiene los badges de un usuario específico
    
    Returns:
        list de badges del usuario con información detallada
    """
    
    try:
        # Obtener badges del usuario
        user_badges = await db.user_badges.find({"user_id": user_id}).to_list(length=None)
        
        if not user_badges:
            return []
        
        # Obtener información completa de cada badge
        badges_detallados = []
        for ub in user_badges:
            badge = await db.badges.find_one({"id": ub['badge_id']})
            if badge:
                badges_detallados.append({
                    "nombre": badge.get('nombre'),
                    "descripcion": badge.get('descripcion'),
                    "icono": badge.get('icono'),
                    "rareza": badge.get('rareza'),
                    "obtenido_en": ub.get('obtenido_en')
                })
        
        return badges_detallados
        
    except Exception as e:
        logger.error(f"Error obteniendo badges del usuario: {e}")
        return []


async def actualizar_racha(db: AsyncIOMotorDatabase, user_id: str):
    """
    Actualiza la racha de días consecutivos del usuario
    
    Returns:
        dict con información de la racha
    """
    
    try:
        user = await db.users.find_one({"id": user_id})
        if not user:
            return {"success": False, "message": "Usuario no encontrado"}
        
        ultima_actividad = user.get('ultima_actividad')
        racha_actual = user.get('racha_dias', 0)
        
        ahora = datetime.now(timezone.utc)
        
        # Si es el primer día o no tiene actividad previa
        if not ultima_actividad:
            nueva_racha = 1
        else:
            # Asegurar que ultima_actividad tenga timezone
            if isinstance(ultima_actividad, str):
                ultima_actividad = datetime.fromisoformat(ultima_actividad.replace('Z', '+00:00'))
            elif ultima_actividad.tzinfo is None:
                # Si no tiene timezone, asumir UTC
                ultima_actividad = ultima_actividad.replace(tzinfo=timezone.utc)
            
            # Calcular días desde última actividad
            dias_diferencia = (ahora - ultima_actividad).days
            
            if dias_diferencia == 0:
                # Mismo día, mantener racha
                nueva_racha = racha_actual
            elif dias_diferencia == 1:
                # Día consecutivo, aumentar racha
                nueva_racha = racha_actual + 1
            else:
                # Se rompió la racha
                nueva_racha = 1
        
        # Actualizar
        await db.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "racha_dias": nueva_racha,
                    "ultima_actividad": ahora
                }
            }
        )
        
        # Si alcanzó 7 o 30 días, dar puntos bonus
        if nueva_racha == 7:
            await otorgar_puntos(db, user_id, PUNTOS_CONFIG['racha_7_dias'], "racha_7_dias", "Racha de 7 días consecutivos")
        elif nueva_racha == 30:
            await otorgar_puntos(db, user_id, PUNTOS_CONFIG['racha_30_dias'], "racha_30_dias", "Racha de 30 días consecutivos")
        
        return {
            "success": True,
            "racha_actual": nueva_racha,
            "racha_anterior": racha_actual
        }
        
    except Exception as e:
        logger.error(f"Error actualizando racha: {e}")
        return {"success": False, "error": str(e)}
