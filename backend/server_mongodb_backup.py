from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
from telegram_bot import telegram_notifier, notificar_pregunta_dia
from telegram_webhook import create_telegram_app, set_database, start_bot_polling
from coach_ia_integration import coach_ia, consultar_coach, llamar_coach
import tempfile
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Variable global para el bot de Telegram
telegram_app = None

@app.on_event("startup")
async def startup_event():
    """Inicializa servicios al arrancar el servidor"""
    global telegram_app
    
    # Configurar database para telegram_webhook
    set_database(db)
    
    # Iniciar bot de Telegram en background
    try:
        telegram_app = await start_bot_polling()
        if telegram_app:
            logging.info("✅ Bot de Telegram iniciado correctamente")
        else:
            logging.warning("⚠️ Bot de Telegram no configurado (falta token)")
    except Exception as e:
        logging.error(f"❌ Error iniciando bot de Telegram: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpia recursos al apagar el servidor"""
    global telegram_app
    
    if telegram_app:
        try:
            from telegram_webhook import stop_bot_polling
            await stop_bot_polling(telegram_app)
            logging.info("Bot de Telegram detenido")
        except Exception as e:
            logging.error(f"Error deteniendo bot: {e}")

# ============= MODELS =============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    nombre: str
    apellido: str
    cargo: Optional[str] = None
    division: Optional[str] = None
    experiencia_anos: Optional[int] = None
    tamano_equipo: Optional[int] = None
    desafios_equipo: Optional[str] = None
    objetivos_personales: Optional[str] = None
    valores_compromiso: Optional[str] = None
    fecha_registro: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    onboarding_completado: bool = False
    semana_actual: int = 1
    bloque_actual: int = 1
    telegram_chat_id: Optional[str] = None
    notificaciones_activas: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    apellido: str

class UserOnboarding(BaseModel):
    cargo: str
    division: str
    experiencia_anos: int
    tamano_equipo: int
    desafios_equipo: str
    objetivos_personales: str
    valores_compromiso: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class RespuestaLMV(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    semana: int
    bloque: int
    numero_envio: str  # P1, P2, P3
    pregunta: str
    respuesta_texto: Optional[str] = None
    respuesta_audio_url: Optional[str] = None
    feedback_ia: Optional[str] = None
    puntuacion: Optional[int] = None
    fecha_respuesta: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RespuestaCreate(BaseModel):
    pregunta: str
    respuesta_texto: Optional[str] = None
    respuesta_audio_url: Optional[str] = None

class EvaluacionMensual(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    mes: int
    bloque: int
    metricas: dict  # comunicacion, feedback, gestion_conflictos, etc
    resumen_ia: str
    recomendaciones: List[str]
    fecha_evaluacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostComunidad(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    autor_nombre: str
    contenido: str
    tags: List[str] = []
    likes: int = 0
    comentarios: int = 0
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PostCreate(BaseModel):
    contenido: str
    tags: List[str] = []

class CoachIARequest(BaseModel):
    mensaje: str
    contexto: Optional[str] = None

# ============= AUTH FUNCTIONS =============

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============= PREGUNTAS L-M-V =============

# Importar las 144 preguntas completas (48 semanas)
from preguntas_lmv_completas import PREGUNTAS_LMV_COMPLETAS

PREGUNTAS_LMV = PREGUNTAS_LMV_COMPLETAS

# ============= AUTH ROUTES =============

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        nombre=user_data.nombre,
        apellido=user_data.apellido
    )
    
    # Hash password and store separately
    hashed_password = get_password_hash(user_data.password)
    user_doc = user.model_dump()
    user_doc['timestamp'] = user_doc.pop('fecha_registro').isoformat()
    user_doc['hashed_password'] = hashed_password
    
    await db.users.insert_one(user_doc)
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_obj = User(**{k: v for k, v in user.items() if k != 'hashed_password'})
    access_token = create_access_token(data={"sub": user_obj.id})
    
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.put("/auth/onboarding")
async def complete_onboarding(data: UserOnboarding, current_user: User = Depends(get_current_user)):
    update_data = data.model_dump()
    update_data['onboarding_completado'] = True
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": update_data}
    )
    
    return {"message": "Onboarding completed successfully"}

# ============= L-M-V ROUTES =============

@api_router.get("/lmv/pregunta-dia")
async def get_pregunta_dia(current_user: User = Depends(get_current_user)):
    """Obtiene la pregunta del día basada en la semana actual"""
    semana = current_user.semana_actual
    
    # Determinar día de la semana (L=P1, M=P2, V=P3)
    dia_semana = datetime.now(timezone.utc).weekday()
    if dia_semana == 0:  # Lunes
        numero_envio = "P1"
    elif dia_semana == 2:  # Miércoles
        numero_envio = "P2"
    elif dia_semana == 4:  # Viernes
        numero_envio = "P3"
    else:
        return {"mensaje": "Hoy no hay pregunta programada. Las preguntas llegan los Lunes, Miércoles y Viernes."}
    
    # Check if already answered
    respuesta_existente = await db.respuestas_lmv.find_one({
        "user_id": current_user.id,
        "semana": semana,
        "numero_envio": numero_envio
    })
    
    if respuesta_existente:
        return {"mensaje": "Ya respondiste la pregunta de hoy", "respondida": True}
    
    pregunta_data = PREGUNTAS_LMV.get(semana, {}).get(numero_envio)
    if not pregunta_data:
        # Si no hay pregunta para esta semana específica, mostrar mensaje
        if semana > 48:
            return {"mensaje": "¡Felicidades! Has completado el programa de 48 semanas"}
        return {"mensaje": "No hay pregunta disponible para esta semana"}
    
    return {
        "semana": semana,
        "numero_envio": numero_envio,
        "pregunta": pregunta_data["pregunta"],
        "tipo": pregunta_data["tipo"],
        "competencia": pregunta_data["competencia"],
        "respondida": False
    }

@api_router.post("/lmv/responder")
async def responder_pregunta(respuesta: RespuestaCreate, current_user: User = Depends(get_current_user)):
    """Envía respuesta a la pregunta del día"""
    semana = current_user.semana_actual
    dia_semana = datetime.now(timezone.utc).weekday()
    
    if dia_semana == 0:
        numero_envio = "P1"
    elif dia_semana == 2:
        numero_envio = "P2"
    elif dia_semana == 4:
        numero_envio = "P3"
    else:
        raise HTTPException(status_code=400, detail="Hoy no es día de respuesta")
    
    respuesta_lmv = RespuestaLMV(
        user_id=current_user.id,
        semana=semana,
        bloque=current_user.bloque_actual,
        numero_envio=numero_envio,
        pregunta=respuesta.pregunta,
        respuesta_texto=respuesta.respuesta_texto,
        respuesta_audio_url=respuesta.respuesta_audio_url
    )
    
    doc = respuesta_lmv.model_dump()
    doc['fecha_respuesta'] = doc['fecha_respuesta'].isoformat()
    
    await db.respuestas_lmv.insert_one(doc)
    
    return {"message": "Respuesta guardada exitosamente", "id": respuesta_lmv.id}

@api_router.get("/lmv/mis-respuestas")
async def get_mis_respuestas(current_user: User = Depends(get_current_user)):
    """Obtiene todas las respuestas del usuario"""
    respuestas = await db.respuestas_lmv.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).sort("semana", -1).to_list(1000)
    
    return respuestas

# ============= METRICAS ROUTES =============

@api_router.get("/metricas/progreso")
async def get_metricas_progreso(current_user: User = Depends(get_current_user)):
    """Obtiene métricas de progreso del usuario"""
    total_respuestas = await db.respuestas_lmv.count_documents({"user_id": current_user.id})
    
    # Métricas simuladas (en producción se calcularían con IA)
    metricas = {
        "comunicacion_efectiva": 78,
        "feedback_constructivo": 65,
        "gestion_conflictos": 72,
        "delegacion": 58,
        "inteligencia_emocional": 81,
        "pensamiento_estrategico": 70,
        "total_respuestas": total_respuestas,
        "semana_actual": current_user.semana_actual,
        "bloque_actual": current_user.bloque_actual,
        "progreso_programa": int((current_user.semana_actual / 48) * 100)
    }
    
    return metricas

# ============= COMUNIDAD ROUTES =============

@api_router.get("/comunidad/posts")
async def get_posts_comunidad(skip: int = 0, limit: int = 20):
    """Obtiene posts de la comunidad"""
    posts = await db.posts_comunidad.find(
        {},
        {"_id": 0}
    ).sort("fecha_creacion", -1).skip(skip).limit(limit).to_list(limit)
    
    return posts

@api_router.post("/comunidad/posts")
async def crear_post(post_data: PostCreate, current_user: User = Depends(get_current_user)):
    """Crea un nuevo post en la comunidad"""
    post = PostComunidad(
        user_id=current_user.id,
        autor_nombre=f"{current_user.nombre} {current_user.apellido}",
        contenido=post_data.contenido,
        tags=post_data.tags
    )
    
    doc = post.model_dump()
    doc['fecha_creacion'] = doc['fecha_creacion'].isoformat()
    
    await db.posts_comunidad.insert_one(doc)
    
    return post

# ============= COACH IA ROUTES =============

@api_router.post("/coach/consultar")
async def consultar_coach_endpoint(request: CoachIARequest, current_user: User = Depends(get_current_user)):
    """Consulta al Coach IA con GPT-4o"""
    contexto_usuario = {
        "nombre": current_user.nombre,
        "cargo": current_user.cargo,
        "division": current_user.division,
        "experiencia_anos": current_user.experiencia_anos,
        "tamano_equipo": current_user.tamano_equipo,
        "desafios_equipo": current_user.desafios_equipo,
        "objetivos_personales": current_user.objetivos_personales
    }
    
    respuesta = await consultar_coach(request.mensaje, contexto_usuario)
    
    return {
        "respuesta": respuesta,
        "contexto_usado": request.contexto or "general"
    }

@api_router.post("/coach/audio")
async def procesar_audio_coach(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Procesa audio del usuario, transcribe y envía al Coach IA"""
    try:
        # Guardar audio temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Transcribir audio
        with open(temp_path, "rb") as audio_file:
            transcripcion = await coach_ia.transcribir_audio(audio_file)
        
        # Eliminar archivo temporal
        os.unlink(temp_path)
        
        # Consultar al coach con el texto transcrito
        contexto_usuario = {
            "nombre": current_user.nombre,
            "cargo": current_user.cargo,
            "division": current_user.division,
            "experiencia_anos": current_user.experiencia_anos,
            "tamano_equipo": current_user.tamano_equipo,
            "desafios_equipo": current_user.desafios_equipo,
            "objetivos_personales": current_user.objetivos_personales
        }
        
        respuesta = await consultar_coach(transcripcion, contexto_usuario)
        
        return {
            "transcripcion": transcripcion,
            "respuesta": respuesta,
            "success": True
        }
        
    except Exception as e:
        logging.error(f"Error procesando audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar audio: {str(e)}")

@api_router.post("/coach/llamar")
async def llamar_coach_vapi(current_user: User = Depends(get_current_user)):
    """Inicia llamada de voz con el Coach IA usando VAPI"""
    if not current_user.telegram_chat_id:  # O agregar campo telefono
        raise HTTPException(status_code=400, detail="Número de teléfono no configurado")
    
    contexto_usuario = {
        "nombre": current_user.nombre,
        "cargo": current_user.cargo,
        "division": current_user.division,
        "desafios_equipo": current_user.desafios_equipo
    }
    
    resultado = await llamar_coach(current_user.telegram_chat_id, contexto_usuario)
    
    if resultado["success"]:
        return {"message": "Llamada iniciada", "call_id": resultado["call"].get("id")}
    else:
        raise HTTPException(status_code=500, detail=resultado["error"])

# ============= TELEGRAM ROUTES =============

class TelegramConfig(BaseModel):
    telegram_chat_id: str
    notificaciones_activas: bool = True

class TelegramVincular(BaseModel):
    codigo_vinculacion: str

@api_router.post("/telegram/vincular")
async def vincular_telegram(vinculo: TelegramVincular, current_user: User = Depends(get_current_user)):
    """Vincula cuenta de usuario con Telegram usando código"""
    # El código tiene formato: EVOLL-{chat_id}
    if not vinculo.codigo_vinculacion.startswith("EVOLL-"):
        raise HTTPException(status_code=400, detail="Código de vinculación inválido")
    
    try:
        chat_id = vinculo.codigo_vinculacion.replace("EVOLL-", "")
        
        # Verificar que el chat_id no esté ya vinculado a otra cuenta
        existing_user = await db.users.find_one({"telegram_chat_id": chat_id, "id": {"$ne": current_user.id}})
        if existing_user:
            raise HTTPException(status_code=400, detail="Este código ya está vinculado a otra cuenta")
        
        # Vincular
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {
                "telegram_chat_id": chat_id,
                "notificaciones_activas": True
            }}
        )
        
        # Enviar mensaje de confirmación
        pregunta_test = {
            "semana": "✅",
            "numero_envio": "",
            "tipo": "Confirmación",
            "competencia": "Sistema",
            "pregunta": f"¡Hola {current_user.nombre}! Tu cuenta ha sido vinculada exitosamente. Ahora recibirás notificaciones del programa EvoLL aquí. 🎉"
        }
        
        link = "https://coach-ai-9.preview.emergentagent.com/dashboard"
        await notificar_pregunta_dia(chat_id, pregunta_test, link)
        
        return {"message": "Telegram vinculado exitosamente", "chat_id": chat_id}
        
    except Exception as e:
        logging.error(f"Error vinculando Telegram: {e}")
        raise HTTPException(status_code=500, detail=f"Error al vincular: {str(e)}")

@api_router.post("/telegram/configurar")
async def configurar_telegram(config: TelegramConfig, current_user: User = Depends(get_current_user)):
    """Configura Telegram para recibir notificaciones"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {
            "telegram_chat_id": config.telegram_chat_id,
            "notificaciones_activas": config.notificaciones_activas
        }}
    )
    
    return {"message": "Telegram configurado exitosamente"}

@api_router.post("/telegram/test")
async def test_telegram(current_user: User = Depends(get_current_user)):
    """Envía notificación de prueba"""
    if not current_user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram no configurado")
    
    pregunta_test = {
        "semana": 1,
        "numero_envio": "P1",
        "tipo": "Test",
        "competencia": "Sistema de notificaciones",
        "pregunta": "Esta es una notificación de prueba. Si la recibes, ¡todo funciona correctamente! 🎉"
    }
    
    link = "https://coach-ai-9.preview.emergentagent.com/dashboard"
    
    resultado = await notificar_pregunta_dia(current_user.telegram_chat_id, pregunta_test, link)
    
    if resultado:
        return {"message": "Notificación de prueba enviada"}
    else:
        raise HTTPException(status_code=500, detail="Error enviando notificación")

@api_router.get("/telegram/status")
async def telegram_status():
    """Verifica estado del bot de Telegram"""
    status = await telegram_notifier.verificar_bot()
    return {
        "activo": status,
        "bot_configurado": telegram_notifier.bot is not None
    }

@api_router.delete("/telegram/desvincular")
async def desvincular_telegram(current_user: User = Depends(get_current_user)):
    """Desvincula la cuenta de Telegram"""
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {
            "telegram_chat_id": None,
            "notificaciones_activas": False
        }}
    )
    
    return {"message": "Telegram desvinculado exitosamente"}

# ============= BASIC ROUTES =============

@api_router.get("/")
async def root():
    return {"message": "EvoLL API - Plataforma de Liderazgo Orenes"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()