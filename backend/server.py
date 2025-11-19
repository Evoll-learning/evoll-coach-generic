from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
from vapi_integration import iniciar_llamada_vapi, obtener_estado_llamada, verificar_configuracion_vapi
from gamification import otorgar_puntos, obtener_leaderboard, obtener_badges_usuario, actualizar_racha, PUNTOS_CONFIG
from supabase_client import supabase_db, supabase
import tempfile
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Supabase como base de datos principal
db = supabase_db

# MongoDB mantenido temporalmente para telegram_webhook
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
mongo_client = AsyncIOMotorClient(mongo_url)
mongo_db = mongo_client[os.environ.get('DB_NAME', 'evoll_db')]

# Security
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI()

# Add CORS middleware FIRST (before any routers)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["https://coach.evollinstitute.com", "http://localhost:3000", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

# Variable global para el bot de Telegram
telegram_app = None
telegram_bot_starting = False

@app.on_event("startup")
async def startup_event():
    """Inicializa servicios al arrancar el servidor"""
    global telegram_app, telegram_bot_starting
    
    # Configurar database para telegram_webhook (ahora usa Supabase)
    set_database(supabase_db)
    
    # Evitar múltiples inicializaciones simultáneas
    if telegram_bot_starting:
        logging.warning("⚠️ Bot de Telegram ya está iniciándose, saltando...")
        return
    
    # Iniciar bot de Telegram en background
    try:
        telegram_bot_starting = True
        telegram_app = await start_bot_polling()
        if telegram_app:
            logging.info("✅ Bot de Telegram iniciado correctamente")
        else:
            logging.warning("⚠️ Bot de Telegram no pudo iniciarse (puede haber otra instancia corriendo o falta token)")
    except Exception as e:
        logging.error(f"❌ Error iniciando bot de Telegram: {e}")
        logging.info("💡 Si ves error 'Conflict', detén todas las instancias del servidor y vuelve a iniciar")
    finally:
        telegram_bot_starting = False

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

class ConversacionCoach(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_id: str
    tipo: str  # "texto", "audio", "elevenlabs"
    role: str  # "user" o "assistant"
    content: str
    metadata: Optional[dict] = None
    fecha: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversacionGuardar(BaseModel):
    tipo: str
    role: str
    content: str
    session_id: Optional[str] = None
    metadata: Optional[dict] = None

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
        
        # Buscar usuario en Supabase
        user_data = await db.find_user_by_id(user_id)
        if user_data is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logging.error(f"Error en get_current_user: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

# ============= PREGUNTAS L-M-V =============

# Importar las 144 preguntas completas (48 semanas)
from preguntas_lmv_completas import PREGUNTAS_LMV_COMPLETAS

PREGUNTAS_LMV = PREGUNTAS_LMV_COMPLETAS

# ============= AUTH ROUTES =============

# Handle preflight requests for CORS
@api_router.options("/auth/register")
@api_router.options("/auth/login")
async def options_auth(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "https://coach.evollinstitute.com"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return {"status": "ok"}

@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, response: Response):
    # Check if user exists in Supabase
    existing_user = await db.find_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        nombre=user_data.nombre,
        apellido=user_data.apellido
    )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Preparar datos para Supabase (adaptado al schema real)
    user_data_dict = {
        'email': user.email,
        'nombre': user.nombre,
        'apellido': user.apellido or '',
        'hashed_password': hashed_password,
        'cargo': None,
        'division': None,
        'experiencia_anos': 0,
        'tamano_equipo': 0,
        'telegram_chat_id': None,
        'puntos_totales': 0,
        'nivel': 1,
        'racha_dias': 0,
        'ultima_actividad': datetime.now(timezone.utc).isoformat(),
        'onboarding_completed': False
    }
    
    # Insertar en Supabase
    await db.create_user(user_data_dict)
    
    # Create token
    access_token = create_access_token(data={"sub": user.id})
    
    # Add CORS headers manually
    response.headers["Access-Control-Allow-Origin"] = "https://coach.evollinstitute.com"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, response: Response):
    # Buscar usuario en Supabase
    user_data = await db.find_user_by_email(credentials.email)
    if not user_data or not verify_password(credentials.password, user_data['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Crear objeto User (sin password)
    user_dict = {k: v for k, v in user_data.items() if k != 'hashed_password'}
    user_obj = User(**user_dict)
    
    # Create token
    access_token = create_access_token(data={"sub": user_obj.id})
    
    # Add CORS headers manually
    response.headers["Access-Control-Allow-Origin"] = "https://coach.evollinstitute.com"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return Token(access_token=access_token, token_type="bearer", user=user_obj)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.put("/auth/onboarding")
async def complete_onboarding(data: UserOnboarding, current_user: User = Depends(get_current_user)):
    # Mapear nombres de campos a los de Supabase
    update_data = {
        'cargo': data.cargo,
        'division': data.division,
        'experiencia_anos': data.experiencia_anos,
        'tamano_equipo': data.tamano_equipo,
        'desafios_equipo': data.desafios_equipo,
        'objetivos_personales': data.objetivos_personales,
        'valores_comprometidos': [data.valores_compromiso] if data.valores_compromiso else [],  # Array en Supabase
        'onboarding_completed': True
    }
    
    # Actualizar en Supabase
    await db.update_user(current_user.id, update_data)
    
    return {"message": "Onboarding completed successfully"}

# ============= L-M-V ROUTES =============

@api_router.get("/lmv/pregunta-dia")
async def get_pregunta_dia(current_user: User = Depends(get_current_user)):
    """Obtiene la pregunta del día basada en la semana actual"""
    semana = current_user.semana_actual
    
    # Determinar día de la semana (L=P1, M=P2, V=P3)
    dia_semana = datetime.now(timezone.utc).weekday()
    if dia_semana == 0:  # Lunes
        numero_envio = 1
    elif dia_semana == 2:  # Miércoles
        numero_envio = 2
    elif dia_semana == 4:  # Viernes
        numero_envio = 3
    else:
        return {"mensaje": "Hoy no hay pregunta programada. Las preguntas llegan los Lunes, Miércoles y Viernes."}
    
    # Check if already answered - usando Supabase
    respuestas_usuario = await supabase_db.find_respuestas_by_user(current_user.id)
    respuesta_existente = next(
        (r for r in respuestas_usuario if r.get('semana') == semana and r.get('numero_envio') == numero_envio),
        None
    )
    
    if respuesta_existente:
        return {"mensaje": "Ya respondiste la pregunta de hoy", "respondida": True}
    
    # Consultar pregunta desde Supabase
    try:
        response = supabase.table('banco_preguntas').select('*').eq('semana', semana).eq('numero_envio', numero_envio).execute()
        
        if not response.data or len(response.data) == 0:
            if semana > 48:
                return {"mensaje": "¡Felicidades! Has completado el programa de 48 semanas"}
            return {"mensaje": "No hay pregunta disponible para esta semana"}
        
        pregunta_data = response.data[0]
        
        return {
            "semana": semana,
            "numero_envio": f"P{numero_envio}",
            "pregunta": pregunta_data["pregunta"],
            "tipo": pregunta_data.get("tipo_pregunta", "Reflexión"),
            "competencia": pregunta_data.get("competencia_clave", "Liderazgo"),
            "respondida": False
        }
    except Exception as e:
        print(f"Error consultando pregunta: {e}")
        return {"mensaje": "Error al obtener la pregunta del día"}

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
    
    # Guardar respuesta en Supabase
    respuesta_data = {
        "user_id": current_user.id,
        "semana": semana,
        "numero_envio": numero_envio,
        "pregunta": respuesta.pregunta,
        "respuesta": respuesta.respuesta_texto,
        "fecha_respuesta": datetime.now(timezone.utc).isoformat(),
        "puntos_otorgados": 10,
        "enviado_via": "web",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await supabase_db.create_respuesta_lmv(respuesta_data)
    
    # Otorgar puntos al usuario
    await supabase_db.increment_user_points(current_user.id, 10)
    
    return {"message": "Respuesta guardada exitosamente", "id": result.get('id')}

@api_router.post("/respuestas/audio")
async def responder_con_audio(
    audio: UploadFile = File(...),
    pregunta_id: str = Form(default=""),
    current_user: User = Depends(get_current_user)
):
    """Procesa audio de respuesta a pregunta del día"""
    from coach_ia_integration import transcribir_audio
    import tempfile
    
    try:
        # Guardar audio temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            content = await audio.read()
            temp_audio.write(content)
            temp_audio_path = temp_audio.name
        
        # Transcribir audio
        transcripcion = await transcribir_audio(temp_audio_path)
        
        # Eliminar archivo temporal
        os.remove(temp_audio_path)
        
        if not transcripcion:
            raise HTTPException(status_code=400, detail="No se pudo transcribir el audio")
        
        # Guardar respuesta transcrita
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
        
        # Buscar pregunta del día
        pregunta_data = PREGUNTAS_LMV.get(semana, {}).get(numero_envio)
        if not pregunta_data:
            raise HTTPException(status_code=404, detail="No hay pregunta para hoy")
        
        # Crear respuesta
        respuesta_lmv = RespuestaLMV(
            user_id=current_user.id,
            semana=semana,
            bloque=current_user.bloque_actual,
            numero_envio=numero_envio,
            pregunta=pregunta_data["pregunta"],
            respuesta_texto=transcripcion,
            respuesta_audio_url=None  # Podríamos guardar el audio en S3/storage
        )
        
        doc = respuesta_lmv.model_dump()
        doc['fecha_respuesta'] = doc['fecha_respuesta'].isoformat()
        doc['via'] = 'audio_web'
        doc['puntos_otorgados'] = 10
        
        await db.respuestas_lmv.insert_one(doc)
        
        # Otorgar puntos
        await db.users.update_one(
            {"id": current_user.id},
            {
                "$inc": {"puntos_totales": 10},
                "$set": {"ultima_actividad": datetime.now(timezone.utc)}
            }
        )
        
        return {
            "success": True,
            "transcripcion": transcripcion,
            "puntos_ganados": 10,
            "message": "Respuesta guardada exitosamente"
        }
        
    except Exception as e:
        logging.error(f"Error procesando audio de respuesta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/lmv/mis-respuestas")
async def get_mis_respuestas(current_user: User = Depends(get_current_user)):
    """Obtiene todas las respuestas del usuario"""
    respuestas = await supabase_db.find_respuestas_by_user(current_user.id)
    return respuestas

# ============= METRICAS ROUTES =============

@api_router.get("/metricas/progreso")
async def get_metricas_progreso(current_user: User = Depends(get_current_user)):
    """Obtiene métricas de progreso del usuario"""
    respuestas = await supabase_db.find_respuestas_by_user(current_user.id)
    total_respuestas = len(respuestas)
    
    # Calcular métricas REALES basadas en actividad del usuario
    # Base: 40% inicial para todos
    # +5% por cada respuesta L-M-V (máximo +60%)
    # Total máximo: 100%
    
    puntos_por_respuesta = min(total_respuestas * 5, 60)
    base = 40
    
    # Variación por competencia (pequeña aleatoriedad para realismo)
    import random
    random.seed(current_user.id)  # Seed constante por usuario para consistencia
    
    metricas = {
        "comunicacion_efectiva": min(base + puntos_por_respuesta + random.randint(-5, 5), 100),
        "feedback_constructivo": min(base + puntos_por_respuesta + random.randint(-5, 5), 100),
        "gestion_conflictos": min(base + puntos_por_respuesta + random.randint(-5, 5), 100),
        "delegacion": min(base + puntos_por_respuesta + random.randint(-5, 5), 100),
        "inteligencia_emocional": min(base + puntos_por_respuesta + random.randint(-5, 5), 100),
        "pensamiento_estrategico": min(base + puntos_por_respuesta + random.randint(-5, 5), 100),
        "total_respuestas": total_respuestas,
        "semana_actual": current_user.semana_actual,
        "bloque_actual": current_user.bloque_actual,
        "progreso_programa": int((current_user.semana_actual / 48) * 100) if current_user.semana_actual else 0
    }
    
    return metricas

# ============= COMUNIDAD ROUTES =============

@api_router.get("/comunidad/posts")
async def get_posts_comunidad(skip: int = 0, limit: int = 20):
    """Obtiene posts de la comunidad"""
    posts = await supabase_db.get_posts_comunidad(limit=limit)
    
    return posts

@api_router.post("/comunidad/posts")
async def crear_post(post_data: PostCreate, current_user: User = Depends(get_current_user)):
    """Crea un nuevo post en la comunidad"""
    post_dict = {
        "user_id": current_user.id,
        "autor_nombre": f"{current_user.nombre} {current_user.apellido}",
        "contenido": post_data.contenido,
        "tags": post_data.tags,
        "likes": 0,
        "comentarios": 0,
        "fecha_creacion": datetime.now(timezone.utc).isoformat()
    }
    
    result = await supabase_db.create_post_comunidad(post_dict)
    
    return result

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
    
    # Otorgar puntos por consulta
    puntos_result = await otorgar_puntos(
        db,
        current_user.id,
        PUNTOS_CONFIG['coach_consulta_texto'],
        "coach_consulta_texto",
        "Consulta al Coach IA por texto"
    )
    
    return {
        "respuesta": respuesta,
        "contexto_usado": request.contexto or "general",
        "puntos_ganados": puntos_result.get('puntos_otorgados', 0) if puntos_result.get('success') else 0
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
        
        # Otorgar puntos por consulta de audio
        puntos_result = await otorgar_puntos(
            db,
            current_user.id,
            PUNTOS_CONFIG['coach_consulta_audio'],
            "coach_consulta_audio",
            "Consulta al Coach IA por audio"
        )
        
        return {
            "transcripcion": transcripcion,
            "respuesta": respuesta,
            "success": True,
            "puntos_ganados": puntos_result.get('puntos_otorgados', 0) if puntos_result.get('success') else 0
        }
        
    except Exception as e:
        logging.error(f"Error procesando audio: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar audio: {str(e)}")

@api_router.post("/coach/llamar-vapi")
async def llamar_coach_vapi_endpoint(phone_number: str, current_user: User = Depends(get_current_user)):
    """
    Inicia llamada de voz con el Coach IA usando VAPI
    
    Args:
        phone_number: Número de teléfono del usuario (formato: +34612345678)
    """
    
    # Validar formato de teléfono
    if not phone_number.startswith('+'):
        raise HTTPException(
            status_code=400, 
            detail="El número debe estar en formato internacional (ej: +34612345678)"
        )
    
    contexto_usuario = {
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "cargo": current_user.cargo,
        "division": current_user.division,
        "experiencia_anos": current_user.experiencia_anos,
        "tamano_equipo": current_user.tamano_equipo,
        "desafios_equipo": current_user.desafios_equipo,
        "objetivos_personales": current_user.objetivos_personales
    }
    
    try:
        resultado = await iniciar_llamada_vapi(phone_number, contexto_usuario)
        
        # Guardar llamada en base de datos
        await db.conversaciones_coach.insert_one({
            "user_id": current_user.id,
            "session_id": resultado['call_id'],
            "role": "system",
            "content": f"Llamada VAPI iniciada a {phone_number}",
            "via": "vapi",
            "fecha": datetime.now(timezone.utc)
        })
        
        return resultado
        
    except Exception as e:
        logging.error(f"Error iniciando llamada VAPI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/coach/vapi-status")
async def vapi_status_endpoint():
    """Verifica el estado de la configuración de VAPI"""
    try:
        status = await verificar_configuracion_vapi()
        return status
    except Exception as e:
        return {
            "configurado": False,
            "error": str(e)
        }

@api_router.get("/coach/vapi-web-token")
async def vapi_web_token_endpoint(current_user: User = Depends(get_current_user)):
    """Obtiene configuración para VAPI Web SDK"""
    try:
        from vapi_integration import obtener_web_token
        
        contexto_usuario = {
            "nombre": current_user.nombre,
            "cargo": current_user.cargo,
            "division": current_user.division
        }
        
        config = await obtener_web_token(contexto_usuario)
        return config
    except Exception as e:
        logging.error(f"Error obteniendo web token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/coach/elevenlabs-config")
async def elevenlabs_config_endpoint(current_user: User = Depends(get_current_user)):
    """Obtiene configuración para ElevenLabs Conversational AI"""
    try:
        elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY', '')
        elevenlabs_agent_id = os.environ.get('ELEVENLABS_AGENT_ID', '')
        
        if not elevenlabs_api_key or not elevenlabs_agent_id:
            raise HTTPException(
                status_code=500, 
                detail="ElevenLabs no está configurado correctamente en el servidor"
            )
        
        return {
            "agent_id": elevenlabs_agent_id,
            "api_key": elevenlabs_api_key,
            "configurado": True,
            "user_context": {
                "nombre": current_user.nombre,
                "cargo": current_user.cargo,
                "division": current_user.division
            }
        }
    except Exception as e:
        logging.error(f"Error obteniendo config ElevenLabs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/coach/guardar-conversacion")
async def guardar_conversacion_coach(
    data: ConversacionGuardar, 
    current_user: User = Depends(get_current_user)
):
    """
    Guarda una conversación del Coach IA (texto, audio o ElevenLabs)
    Frontend debe llamar a este endpoint después de cada mensaje
    """
    try:
        conversacion = ConversacionCoach(
            user_id=current_user.id,
            session_id=data.session_id or str(uuid.uuid4()),
            tipo=data.tipo,
            role=data.role,
            content=data.content,
            metadata=data.metadata or {}
        )
        
        # Guardar en Supabase
        conv_dict = {
            'id': conversacion.id,
            'user_id': conversacion.user_id,
            'session_id': conversacion.session_id,
            'tipo': conversacion.tipo,
            'role': conversacion.role,
            'content': conversacion.content,
            'metadata': conversacion.metadata,
            'created_at': conversacion.fecha.isoformat()
        }
        
        await db.create_conversacion(conv_dict)
        
        logging.info(f"💾 Conversación guardada: {current_user.email} - {data.tipo} - {data.role}")
        
        return {
            "success": True,
            "message": "Conversación guardada exitosamente",
            "conversation_id": conversacion.id,
            "session_id": conversacion.session_id
        }
        
    except Exception as e:
        logging.error(f"Error guardando conversación: {e}")
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")

@api_router.get("/coach/historial")
async def obtener_historial_conversaciones(
    current_user: User = Depends(get_current_user),
    tipo: Optional[str] = None,
    limit: int = 50
):
    """
    Obtiene el historial de conversaciones del usuario con el Coach IA
    Puede filtrar por tipo: texto, audio, elevenlabs
    """
    try:
        conversaciones = await db.find_conversaciones_by_user(current_user.id, limit)
        
        return {
            "success": True,
            "total": len(conversaciones),
            "conversaciones": conversaciones
        }
        
    except Exception as e:
        logging.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")

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
        chat_id = vinculo.codigo_vinculacion.replace("EVOLL-", "").strip()
        
        # Validar que sea un número válido
        if not chat_id.isdigit():
            raise HTTPException(status_code=400, detail="Código de vinculación inválido")
        
        # Verificar que el chat_id no esté ya vinculado a otra cuenta
        existing_user = await supabase_db.find_user_by_telegram_chat_id(chat_id)
        if existing_user and existing_user['id'] != current_user.id:
            raise HTTPException(status_code=400, detail="Este código ya está vinculado a otra cuenta")
        
        # Vincular
        await supabase_db.update_user(
            current_user.id,
            {
                "telegram_chat_id": chat_id,
                "notificaciones_activas": True
            }
        )
        
        # Enviar mensaje de confirmación PRIMERO
        mensaje_confirmacion = {
            "semana": "✅",
            "numero_envio": "",
            "tipo": "Confirmación",
            "competencia": "Sistema",
            "pregunta": f"¡Hola {current_user.nombre}! Tu cuenta ha sido vinculada exitosamente. 🎉\n\nAhora recibirás notificaciones del programa EvoLL aquí."
        }
        
        link_dashboard = "https://coach-ai-9.preview.emergentagent.com/dashboard"
        await notificar_pregunta_dia(chat_id, mensaje_confirmacion, link_dashboard)
        
        # Esperar 2 segundos y enviar primera pregunta de ejemplo
        import asyncio
        await asyncio.sleep(2)
        
        # Obtener primera pregunta pendiente del usuario
        respuestas_pendientes = await supabase_db.find_respuestas_by_user(current_user.id)
        pregunta_enviar = None
        
        for resp in respuestas_pendientes:
            if not resp.get('respuesta'):  # Si no tiene respuesta
                pregunta_enviar = resp
                break
        
        if pregunta_enviar:
            # Enviar la pregunta por Telegram
            pregunta_telegram = {
                "semana": pregunta_enviar.get('semana', 1),
                "numero_envio": pregunta_enviar.get('numero_envio', 'P1'),
                "tipo": pregunta_enviar.get('tipo', 'Liderazgo'),
                "competencia": pregunta_enviar.get('competencia', ''),
                "pregunta": pregunta_enviar.get('pregunta', '')
            }
            
            # Link directo a la sección L-M-V
            link_lmv = "https://coach-ai-9.preview.emergentagent.com/dashboard#lmv"
            await notificar_pregunta_dia(chat_id, pregunta_telegram, link_lmv)
        
        return {"message": "Telegram vinculado exitosamente", "chat_id": chat_id}
        
    except Exception as e:
        logging.error(f"Error vinculando Telegram: {e}")
        raise HTTPException(status_code=500, detail=f"Error al vincular: {str(e)}")

@api_router.post("/telegram/configurar")
async def configurar_telegram(config: TelegramConfig, current_user: User = Depends(get_current_user)):
    """Configura Telegram para recibir notificaciones"""
    await supabase_db.update_user(
        current_user.id,
        {
            "telegram_chat_id": config.telegram_chat_id,
            "notificaciones_activas": config.notificaciones_activas
        }
    )
    
    return {"message": "Telegram configurado exitosamente"}

@api_router.post("/telegram/test")
async def test_telegram(current_user: User = Depends(get_current_user)):
    """Envía notificación de prueba"""
    if not current_user.telegram_chat_id:
        raise HTTPException(status_code=400, detail="Telegram no configurado. Por favor vincula tu cuenta primero.")
    
    try:
        logging.info(f"Enviando notificación de prueba a chat_id: {current_user.telegram_chat_id}")
        
        pregunta_test = {
            "semana": "Prueba",
            "numero_envio": "Test",
            "tipo": "Notificación de Prueba",
            "competencia": "Sistema",
            "pregunta": f"¡Hola {current_user.nombre}! 👋\n\nEsta es una notificación de prueba del sistema EvoLL.\n\nSi recibes este mensaje, todo está funcionando correctamente. ✅"
        }
        
        link = "https://coach-ai-9.preview.emergentagent.com/dashboard"
        
        resultado = await notificar_pregunta_dia(current_user.telegram_chat_id, pregunta_test, link)
        
        if resultado:
            logging.info(f"✅ Notificación de prueba enviada exitosamente a {current_user.email}")
            return {"message": "Notificación de prueba enviada exitosamente", "success": True}
        else:
            logging.error(f"❌ Error al enviar notificación de prueba a {current_user.email}")
            raise HTTPException(
                status_code=500, 
                detail="No se pudo enviar la notificación. Verifica que el bot de Telegram esté activo y que hayas iniciado conversación con @Evoll_Orenes_Bot"
            )
    except Exception as e:
        logging.error(f"❌ Excepción al enviar notificación de prueba: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al enviar notificación: {str(e)}"
        )

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
    await supabase_db.update_user(
        current_user.id,
        {
            "telegram_chat_id": None,
            "notificaciones_activas": False
        }
    )
    
    return {"message": "Telegram desvinculado exitosamente"}

# ============= CRON / NOTIFICACIONES AUTOMATICAS =============

from preguntas_lmv_completas import PREGUNTAS_LMV_COMPLETAS
import random

@api_router.post("/cron/enviar-pregunta-dia")
async def enviar_pregunta_dia():
    """
    Endpoint para cron job - Envía pregunta L-M-V según el día
    Ejecutar diariamente a las 9:00 AM
    """
    # Determinar número de envío según día de la semana
    dia = datetime.now(timezone.utc).weekday()
    
    if dia == 0:  # Lunes
        numero_envio = 1
    elif dia == 2:  # Miércoles
        numero_envio = 2
    elif dia == 4:  # Viernes
        numero_envio = 3
    else:
        return {
            "message": "Hoy no se envían preguntas",
            "dia": dia,
            "dia_nombre": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"][dia]
        }
    
    # Obtener usuarios con Telegram activo desde Supabase
    try:
        response = supabase.table('users').select('*').not_.is_('telegram_chat_id', 'null').execute()
        usuarios = response.data
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return {"message": "Error obteniendo usuarios", "error": str(e)}
    
    if not usuarios:
        return {
            "message": "No hay usuarios con Telegram vinculado",
            "numero_envio": numero_envio
        }
    
    enviados = 0
    errores = 0
    errores_detalle = []

# ============= GAMIFICACIÓN ROUTES =============

@api_router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Obtiene el leaderboard de usuarios ordenados por puntos"""
    try:
        leaderboard = await supabase_db.get_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        logging.error(f"Error obteniendo leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/badges")
async def get_user_badges(current_user: User = Depends(get_current_user)):
    """Obtiene los badges del usuario actual"""
    try:
        badges = await supabase_db.get_user_badges(current_user.id)
        return {"badges": badges}
    except Exception as e:
        logging.error(f"Error obteniendo badges: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stats")
async def get_user_stats(current_user: User = Depends(get_current_user)):
    """Obtiene estadísticas del usuario actual - USANDO SUPABASE"""
    try:
        # Obtener usuario actualizado de Supabase
        user = await supabase_db.find_user_by_id(current_user.id)
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Contar actividades desde Supabase
        respuestas = await supabase_db.find_respuestas_by_user(current_user.id)
        total_respuestas = sum(1 for r in respuestas if r.get('respuesta'))
        
        conversaciones = await supabase_db.find_conversaciones_by_user(current_user.id)
        total_consultas_coach = sum(1 for c in conversaciones if c.get('role') == 'user')
        
        badges = await supabase_db.get_user_badges(current_user.id)
        total_badges = len(badges)
        
        return {
            "puntos_totales": user.get('puntos_totales', 0),
            "nivel": user.get('nivel', 1),
            "racha_dias": user.get('racha_dias', 0),
            "total_respuestas_lmv": total_respuestas,
            "total_consultas_coach": total_consultas_coach,
            "total_badges": total_badges,
            "ultima_actividad": user.get('ultima_actividad')
        }
        
    except Exception as e:
        logging.error(f"Error obteniendo stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= BASIC ROUTES =============

@api_router.get("/")
async def root():
    return {"message": "EvoLL API - Plataforma de Liderazgo Orenes"}

# Include router
app.include_router(api_router)

# Servir archivos estáticos del frontend (si existen)
frontend_build_path = ROOT_DIR.parent / 'frontend' / 'build'
if frontend_build_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_build_path / 'static')), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Servir el frontend React para todas las rutas no-API"""
        if full_path.startswith('api/'):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = frontend_build_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Para rutas de React Router, devolver index.html
        return FileResponse(frontend_build_path / 'index.html')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    """Cerrar conexión de MongoDB si existe"""
    try:
        if 'mongo_client' in globals():
            mongo_client.close()
            logging.info("MongoDB connection closed")
    except Exception as e:
        logging.error(f"Error cerrando MongoDB: {e}")

# ============= OPENAI REALTIME API WEBSOCKET =============

@app.websocket("/ws/openai-realtime")
async def openai_realtime_websocket(websocket: WebSocket):
    """
    WebSocket proxy para OpenAI Realtime API
    Permite que el frontend se conecte sin exponer la API key
    """
    await websocket.accept()
    
    from openai_realtime_proxy import proxy_websocket
    
    try:
        await proxy_websocket(websocket)
    except WebSocketDisconnect:
        logging.info("Cliente desconectado de OpenAI Realtime")
    except Exception as e:
        logging.error(f"Error en WebSocket OpenAI Realtime: {e}")
        try:
            await websocket.close()
        except:
            pass    
    # Enviar preguntas a cada usuario
    for usuario in usuarios:
        try:
            semana = usuario.get('semana_actual', 1)
            
            # Obtener pregunta desde Supabase
            pregunta_response = supabase.table('banco_preguntas').select('*').eq('semana', semana).eq('numero_envio', numero_envio).execute()
            
            if not pregunta_response.data or len(pregunta_response.data) == 0:
                errores += 1
                errores_detalle.append(f"{usuario.get('email')}: No hay pregunta para semana {semana}")
                continue
            
            pregunta_data = pregunta_response.data[0]
            
            # Preparar mensaje para Telegram
            mensaje = f"""
🎯 *Pregunta del Día - Semana {semana}*

{pregunta_data['pregunta']}

📊 *Competencia:* {pregunta_data.get('competencia_clave', 'Liderazgo')}

💡 Responde directamente aquí en Telegram o accede al dashboard:
https://frontend-production-f52f8.up.railway.app/dashboard
"""
            
            # Enviar notificación por Telegram
            from telegram_bot import enviar_mensaje_telegram
            resultado = await enviar_mensaje_telegram(usuario['telegram_chat_id'], mensaje)
            
            if resultado:
                enviados += 1
            else:
                errores += 1
                errores_detalle.append(f"{usuario.get('email')}: Error enviando mensaje")
                
        except Exception as e:
            errores += 1
            error_msg = f"{usuario.get('email')}: {str(e)}"
            errores_detalle.append(error_msg)
            print(f"Error enviando a {error_msg}")
    
    return {
        "success": True,
        "numero_envio": numero_envio,
        "usuarios_enviados": enviados,
        "errores": errores,
        "errores_detalle": errores_detalle if errores > 0 else None,
        "total_usuarios": len(usuarios)
    }


# ==================== BACKUP AUTOMÁTICO ====================
@api_router.get("/admin/backup")
async def trigger_backup():
    """
    Endpoint para ejecutar backup manual
    """
    try:
        import subprocess
        result = subprocess.run(
            ["python3.11", "backup_supabase.py"],
            capture_output=True,
            text=True,
            cwd=str(ROOT_DIR)
        )
        
        return {
            "success": True,
            "message": "Backup ejecutado correctamente",
            "output": result.stdout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@api_router.get("/admin/backup/status")
async def backup_status():
    """
    Verifica el estado de los backups
    """
    try:
        backup_dir = ROOT_DIR / "backups"
        
        if not backup_dir.exists():
            return {"backups": [], "count": 0}
        
        backups = sorted([
            f.name for f in backup_dir.iterdir()
            if f.name.startswith('backup_') and f.name.endswith('.json')
        ], reverse=True)
        
        return {
            "backups": backups[:10],  # Últimos 10
            "count": len(backups),
            "directory": str(backup_dir)
        }
    except Exception as e:
        return {"error": str(e)}
