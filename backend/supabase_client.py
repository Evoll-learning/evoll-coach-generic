"""
Cliente de Supabase para el proyecto EvoLL
Proporciona funciones helpers para interactuar con Supabase de forma similar a MongoDB
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

# Cliente global de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


class SupabaseDB:
    """Clase helper para interactuar con Supabase de forma similar a MongoDB"""
    
    def __init__(self):
        self.client = supabase
    
    # ==================== USERS ====================
    
    async def find_user_by_email(self, email: str) -> Optional[Dict]:
        """Buscar usuario por email"""
        try:
            response = self.client.table('users').select('*').eq('email', email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error buscando usuario: {e}")
            return None
    
    async def find_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Buscar usuario por ID"""
        try:
            response = self.client.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error buscando usuario: {e}")
            return None
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Crear usuario"""
        try:
            response = self.client.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creando usuario: {e}")
            raise e
    
    async def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Actualizar usuario"""
        try:
            response = self.client.table('users').update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            raise e
    
    # ==================== RESPUESTAS L-M-V ====================
    
    async def find_respuestas_by_user(self, user_id: str) -> List[Dict]:
        """Obtener todas las respuestas L-M-V de un usuario"""
        try:
            response = self.client.table('respuestas_lmv').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo respuestas: {e}")
            return []
    
    async def create_respuesta_lmv(self, respuesta_data: Dict) -> Dict:
        """Crear respuesta L-M-V"""
        try:
            response = self.client.table('respuestas_lmv').insert(respuesta_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creando respuesta: {e}")
            raise e
    
    async def update_respuesta_lmv(self, respuesta_id: str, update_data: Dict) -> Dict:
        """Actualizar respuesta L-M-V"""
        try:
            response = self.client.table('respuestas_lmv').update(update_data).eq('id', respuesta_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error actualizando respuesta: {e}")
            raise e
    
    # ==================== CONVERSACIONES COACH ====================
    
    async def create_conversacion(self, conv_data: Dict) -> Dict:
        """Guardar conversación del coach"""
        try:
            response = self.client.table('conversaciones_coach').insert(conv_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error guardando conversación: {e}")
            raise e
    
    async def find_conversaciones_by_user(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Obtener conversaciones de un usuario"""
        try:
            response = self.client.table('conversaciones_coach').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo conversaciones: {e}")
            return []
    
    # ==================== TELEGRAM ====================
    
    async def find_user_by_telegram_chat_id(self, chat_id: str) -> Optional[Dict]:
        """Buscar usuario por telegram_chat_id"""
        try:
            response = self.client.table('users').select('*').eq('telegram_chat_id', chat_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error buscando usuario por telegram: {e}")
            return None
    
    async def find_pending_respuesta_lmv(self, user_id: str) -> Optional[Dict]:
        """Buscar pregunta L-M-V pendiente de respuesta para un usuario"""
        try:
            response = self.client.table('respuestas_lmv').select('*').eq('user_id', user_id).is_('respuesta', 'null').execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error buscando respuesta pendiente: {e}")
            return None
    
    async def update_respuesta_lmv_by_id(self, respuesta_id: str, update_data: Dict) -> Dict:
        """Actualizar respuesta L-M-V por ID"""
        try:
            response = self.client.table('respuestas_lmv').update(update_data).eq('id', respuesta_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error actualizando respuesta por ID: {e}")
            raise e
    
    async def increment_user_points(self, user_id: str, points: int) -> Dict:
        """Incrementar puntos de un usuario y actualizar ultima_actividad"""
        try:
            # Primero obtenemos el usuario actual
            user = await self.find_user_by_id(user_id)
            if not user:
                raise Exception(f"Usuario {user_id} no encontrado")
            
            # Calculamos los nuevos puntos
            new_points = user.get('puntos_totales', 0) + points
            
            # Actualizamos
            update_data = {
                'puntos_totales': new_points,
                'ultima_actividad': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('users').update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error incrementando puntos: {e}")
            raise e
    
    async def create_telegram_message(self, message_data: Dict) -> Dict:
        """Guardar mensaje de Telegram"""
        try:
            response = self.client.table('telegram_messages').insert(message_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error guardando mensaje de telegram: {e}")
            raise e
    
    async def update_user_notificaciones(self, user_id: str, notificaciones_activas: bool) -> Dict:
        """Actualizar estado de notificaciones de un usuario"""
        try:
            update_data = {'notificaciones_activas': notificaciones_activas}
            response = self.client.table('users').update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error actualizando notificaciones: {e}")
            raise e
    
    # ==================== COMUNIDAD ====================
    
    async def create_post_comunidad(self, post_data: Dict) -> Dict:
        """Crear post en la comunidad"""
        try:
            response = self.client.table('posts_comunidad').insert(post_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creando post: {e}")
            raise e
    
    async def get_posts_comunidad(self, limit: int = 50) -> List[Dict]:
        """Obtener posts de la comunidad"""
        try:
            response = self.client.table('posts_comunidad').select('*').order('fecha_creacion', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo posts: {e}")
            return []
    
    async def like_post_comunidad(self, post_id: str) -> Dict:
        """Incrementar likes de un post"""
        try:
            # Get current post
            post = self.client.table('posts_comunidad').select('*').eq('id', post_id).execute()
            if not post.data:
                return None
            
            current_likes = post.data[0].get('likes', 0)
            response = self.client.table('posts_comunidad').update({'likes': current_likes + 1}).eq('id', post_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error dando like: {e}")
            raise e
    
    # ==================== ESTADÍSTICAS ====================
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Obtener leaderboard de usuarios"""
        try:
            response = self.client.table('users').select('id, nombre, apellido, puntos_totales, nivel, racha_dias').order('puntos_totales', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo leaderboard: {e}")
            return []
    
    async def get_user_badges(self, user_id: str) -> List[Dict]:
        """Obtener badges de un usuario"""
        try:
            response = self.client.table('user_badges').select('*, badges(*)').eq('user_id', user_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo badges: {e}")
            return []
    
    async def get_all_badges(self) -> List[Dict]:
        """Obtener todos los badges disponibles"""
        try:
            response = self.client.table('badges').select('*').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error obteniendo badges: {e}")
            return []


# Instancia global
supabase_db = SupabaseDB()
