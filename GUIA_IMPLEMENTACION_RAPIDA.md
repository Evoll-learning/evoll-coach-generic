# 🚀 GUÍA RÁPIDA DE IMPLEMENTACIÓN

**Para agentes futuros o continuación de sesión**

---

## 📋 CHECKLIST DE TAREAS PENDIENTES

### ✅ TAREA 1: Notificaciones Automáticas L-M-V

**Tiempo estimado:** 45 minutos

#### **Paso 1: Crear endpoint de cron** (15 min)

Agregar a `/app/backend/server.py`:

```python
from preguntas_lmv_completas import PREGUNTAS_LMV
from datetime import datetime
import random

@api_router.post("/cron/enviar-pregunta-dia")
async def enviar_pregunta_dia():
    """
    Endpoint llamado diariamente a las 9AM
    Envía pregunta L-M-V según el día de la semana
    """
    # Determinar tipo según día
    dia = datetime.now(timezone.utc).weekday()
    
    tipo_mapa = {
        0: "Liderazgo",      # Lunes
        1: None,
        2: "Management",     # Miércoles
        3: None,
        4: "Valores",        # Viernes
        5: None,
        6: None
    }
    
    tipo = tipo_mapa.get(dia)
    
    if not tipo:
        return {"message": "Hoy no se envían preguntas", "dia": dia}
    
    # Seleccionar pregunta aleatoria del tipo
    preguntas_tipo = [p for p in PREGUNTAS_LMV if p['tipo'] == tipo]
    
    if not preguntas_tipo:
        raise HTTPException(status_code=500, detail="No hay preguntas disponibles")
    
    pregunta = random.choice(preguntas_tipo)
    
    # Obtener usuarios con Telegram activo
    usuarios = await db.users.find({
        "telegram_chat_id": {"$ne": None},
        "notificaciones_activas": True
    }).to_list(length=None)
    
    enviados = 0
    errores = 0
    
    for usuario in usuarios:
        try:
            # Enviar notificación
            link = "https://coach-ai-9.preview.emergentagent.com/dashboard"
            resultado = await notificar_pregunta_dia(
                usuario['telegram_chat_id'],
                pregunta,
                link
            )
            
            if resultado:
                # Guardar en respuestas_lmv
                await db.respuestas_lmv.insert_one({
                    "user_id": usuario['id'],
                    "semana": pregunta['semana'],
                    "tipo": pregunta['tipo'],
                    "competencia": pregunta['competencia'],
                    "pregunta": pregunta['pregunta'],
                    "respuesta": None,
                    "fecha_envio": datetime.now(timezone.utc),
                    "fecha_respuesta": None,
                    "puntos_otorgados": 0
                })
                enviados += 1
        except Exception as e:
            logging.error(f"Error enviando a {usuario['email']}: {e}")
            errores += 1
    
    return {
        "tipo": tipo,
        "pregunta": pregunta['pregunta'],
        "usuarios_enviados": enviados,
        "errores": errores
    }
```

#### **Paso 2: Configurar cron** (10 min)

Crear `/app/backend/cron_notificaciones.py`:

```python
"""
Script para ejecutar como cron job
Ejecutar diariamente a las 9:00 AM
"""

import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = "http://localhost:8001/api"

async def ejecutar_cron():
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(f"{BACKEND_URL}/cron/enviar-pregunta-dia")
            print(f"✅ Cron ejecutado: {response.json()}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(ejecutar_cron())
```

#### **Paso 3: Agregar a crontab** (5 min)

```bash
# Abrir crontab
crontab -e

# Agregar línea (ejecutar diario a las 9AM)
0 9 * * * cd /app/backend && /root/.venv/bin/python cron_notificaciones.py >> /var/log/cron_lmv.log 2>&1
```

#### **Paso 4: Mejorar handler de respuestas** (15 min)

Actualizar `/app/backend/telegram_webhook.py` función `handle_message`:

```python
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para mensajes de texto normales (respuestas del usuario)"""
    chat_id = str(update.effective_chat.id)
    texto = update.message.text
    
    if not db_instance:
        logger.error("Base de datos no disponible")
        return
    
    # Buscar usuario
    user = await db_instance.users.find_one({"telegram_chat_id": chat_id})
    
    if not user:
        await update.message.reply_text(
            "⚠️ Tu cuenta no está vinculada aún.\n\n"
            f"Usa el código `EVOLL-{chat_id}` en tu perfil de la plataforma.",
            parse_mode='Markdown'
        )
        return
    
    # Buscar pregunta pendiente de respuesta
    pregunta_pendiente = await db_instance.respuestas_lmv.find_one({
        "user_id": user['id'],
        "respuesta": None
    })
    
    if pregunta_pendiente:
        # Actualizar respuesta
        await db_instance.respuestas_lmv.update_one(
            {"_id": pregunta_pendiente['_id']},
            {
                "$set": {
                    "respuesta": texto,
                    "fecha_respuesta": update.message.date,
                    "puntos_otorgados": 10
                }
            }
        )
        
        # Otorgar puntos al usuario
        await db_instance.users.update_one(
            {"id": user['id']},
            {"$inc": {"puntos_totales": 10}}
        )
        
        await update.message.reply_text(
            "✅ ¡Respuesta guardada!\n\n"
            "Has ganado +10 puntos 🎉\n\n"
            "_Gracias por tu reflexión sobre liderazgo_",
            parse_mode='Markdown'
        )
    else:
        # Si no hay pregunta pendiente, guardar como mensaje general
        await db_instance.telegram_messages.insert_one({
            "user_id": user['id'],
            "chat_id": chat_id,
            "mensaje": texto,
            "fecha": update.message.date,
            "procesado": False
        })
        
        await update.message.reply_text(
            "📝 Mensaje recibido.\n\n"
            "Si quieres consultar al Coach IA, usa la plataforma web."
        )
    
    logger.info(f"Respuesta procesada de {user.get('nombre')} ({chat_id})")
```

---

### ✅ TAREA 2: VAPI - Llamadas de Voz

**Tiempo estimado:** 30 minutos

#### **Paso 1: Configurar Assistant en VAPI** (10 min)

**MANUAL - Usuario debe hacerlo:**

1. Ve a: https://dashboard.vapi.ai
2. Login con tu cuenta
3. Click "Create Assistant"
4. Configuración:
   - **Name:** EvoLL Coach de Liderazgo
   - **Model:** GPT-4o o GPT-4 Turbo
   - **Voice:** Seleccionar voz en español (ej: es-ES-AlvaroNeural)
   - **First Message:**
     ```
     Hola, soy tu Coach de Liderazgo de EvoLL. ¿En qué puedo ayudarte hoy?
     ```
   - **System Prompt:**
     ```
     Eres un coach ejecutivo experto en liderazgo del Grupo Orenes.
     
     Tu objetivo es ayudar a líderes a:
     - Mejorar su comunicación con equipos
     - Dar y recibir feedback efectivo
     - Gestionar conflictos
     - Desarrollar inteligencia emocional
     - Tomar decisiones estratégicas
     
     Valores de Orenes:
     - 56 años de experiencia
     - Confianza y transparencia
     - Compromiso con las personas
     - Sentimiento familiar
     
     Sé empático, haz preguntas poderosas, y ofrece consejos accionables.
     Mantén un tono profesional pero cercano.
     Habla en español de España.
     ```

5. Guarda el Assistant
6. **COPIAR el Assistant ID** (se ve como: `asst_abc123...`)

#### **Paso 2: Agregar Assistant ID al .env** (2 min)

```bash
# Agregar a /app/backend/.env
VAPI_ASSISTANT_ID="asst_abc123xyz..."
```

#### **Paso 3: Crear integración** (10 min)

Crear `/app/backend/vapi_integration.py`:

```python
"""
Integración con VAPI para llamadas de voz
"""

import os
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.environ.get('VAPI_API_KEY')
VAPI_ASSISTANT_ID = os.environ.get('VAPI_ASSISTANT_ID')
VAPI_BASE_URL = "https://api.vapi.ai"

logger = logging.getLogger(__name__)

async def iniciar_llamada_vapi(phone_number: str, user_context: dict):
    """
    Inicia una llamada con VAPI
    
    Args:
        phone_number: Número de teléfono del usuario (+34...)
        user_context: Contexto del usuario (nombre, cargo, etc)
    
    Returns:
        dict con call_id y status
    """
    
    if not VAPI_API_KEY or not VAPI_ASSISTANT_ID:
        raise Exception("VAPI no está configurado (falta API key o Assistant ID)")
    
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "assistant_id": VAPI_ASSISTANT_ID,
        "phone_number": phone_number,
        "metadata": {
            "user_name": user_context.get('nombre'),
            "user_cargo": user_context.get('cargo'),
            "user_division": user_context.get('division')
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{VAPI_BASE_URL}/call",
                headers=headers,
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Llamada VAPI iniciada: {data.get('id')}")
            
            return {
                "call_id": data.get('id'),
                "status": data.get('status'),
                "success": True
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Error VAPI HTTP: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Error al iniciar llamada: {e.response.text}")
        except Exception as e:
            logger.error(f"Error VAPI: {e}")
            raise Exception(f"Error al iniciar llamada: {str(e)}")
```

#### **Paso 4: Agregar endpoint** (5 min)

Agregar a `/app/backend/server.py`:

```python
from vapi_integration import iniciar_llamada_vapi

class VAPICallRequest(BaseModel):
    phone_number: str  # Formato: +34612345678

@api_router.post("/coach/llamar-vapi")
async def llamar_coach_vapi(request: VAPICallRequest, current_user: User = Depends(get_current_user)):
    """Inicia una llamada de voz con el Coach IA vía VAPI"""
    
    contexto_usuario = {
        "nombre": current_user.nombre,
        "cargo": current_user.cargo,
        "division": current_user.division
    }
    
    try:
        resultado = await iniciar_llamada_vapi(request.phone_number, contexto_usuario)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### **Paso 5: Actualizar frontend** (3 min)

Agregar a `/app/frontend/src/pages/CoachIAPage.js`:

```javascript
const [phoneNumber, setPhoneNumber] = useState('');
const [loadingCall, setLoadingCall] = useState(false);

const handleLlamarCoach = async () => {
  if (!phoneNumber.trim()) {
    toast.error('Por favor ingresa tu número de teléfono');
    return;
  }

  setLoadingCall(true);
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/coach/llamar-vapi`,
      { phone_number: phoneNumber },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    toast.success('¡Llamada iniciada! Recibirás una llamada en breve 📞');
  } catch (error) {
    toast.error('Error al iniciar llamada');
  } finally {
    setLoadingCall(false);
  }
};

// En el JSX, agregar:
<Card className="mb-6 bg-white border-slate-200">
  <CardHeader>
    <CardTitle className="flex items-center space-x-2">
      <Phone className="w-5 h-5 text-green-600" />
      <span>Llamar a mi Coach</span>
    </CardTitle>
    <CardDescription>
      Recibe una llamada telefónica del Coach IA
    </CardDescription>
  </CardHeader>
  <CardContent>
    <div className="flex gap-2">
      <Input
        placeholder="+34 612 345 678"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
        className="flex-1"
      />
      <Button
        onClick={handleLlamarCoach}
        disabled={loadingCall}
        className="bg-green-600 hover:bg-green-700"
      >
        {loadingCall ? 'Llamando...' : '📞 Llamar'}
      </Button>
    </div>
  </CardContent>
</Card>
```

---

### ✅ TAREA 3: Gamificación Básica

**Tiempo estimado:** 30 minutos

#### **Paso 1: Sistema automático de puntos** (15 min)

Crear `/app/backend/gamification.py`:

```python
"""
Sistema de gamificación automático
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

async def otorgar_puntos(db: AsyncIOMotorDatabase, user_id: str, puntos: int, tipo: str, descripcion: str):
    """
    Otorga puntos a un usuario y registra la actividad
    
    Args:
        db: Database instance
        user_id: ID del usuario
        puntos: Cantidad de puntos a otorgar
        tipo: Tipo de actividad (respuesta_lmv, coach_consulta, etc)
        descripcion: Descripción de la actividad
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
                "user_id": user_id,
                "tipo": tipo,
                "descripcion": descripcion,
                "puntos_ganados": puntos,
                "fecha": datetime.now(timezone.utc)
            })
            
            # Verificar si debe subir de nivel
            user = await db.users.find_one({"id": user_id})
            puntos_totales = user.get('puntos_totales', 0)
            nivel_actual = user.get('nivel', 1)
            
            # Lógica simple: cada 100 puntos = 1 nivel
            nuevo_nivel = (puntos_totales // 100) + 1
            
            if nuevo_nivel > nivel_actual:
                await db.users.update_one(
                    {"id": user_id},
                    {"$set": {"nivel": nuevo_nivel}}
                )
                logger.info(f"Usuario {user_id} subió a nivel {nuevo_nivel}")
            
            # Verificar badges
            await verificar_badges(db, user_id, puntos_totales)
            
            logger.info(f"Puntos otorgados: {puntos} a {user_id} por {tipo}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error otorgando puntos: {e}")
        return False

async def verificar_badges(db: AsyncIOMotorDatabase, user_id: str, puntos_totales: int):
    """Verifica y otorga badges según criterios"""
    
    # Obtener badges que el usuario NO tiene
    user_badges = await db.user_badges.find({"user_id": user_id}).to_list(length=None)
    badges_ids_obtenidos = [ub['badge_id'] for ub in user_badges]
    
    # Obtener todos los badges disponibles
    all_badges = await db.badges.find().to_list(length=None)
    
    for badge in all_badges:
        if badge['id'] in badges_ids_obtenidos:
            continue  # Ya lo tiene
        
        # Verificar criterio
        puntos_req = badge.get('puntos_requeridos', 0)
        
        if puntos_totales >= puntos_req:
            # Otorgar badge
            await db.user_badges.insert_one({
                "user_id": user_id,
                "badge_id": badge['id'],
                "obtenido_en": datetime.now(timezone.utc)
            })
            
            logger.info(f"Badge '{badge['nombre']}' otorgado a {user_id}")
            
            # TODO: Notificar al usuario por Telegram
```

#### **Paso 2: Integrar en endpoints** (10 min)

Actualizar endpoints en `/app/backend/server.py`:

```python
from gamification import otorgar_puntos

# En endpoint /coach/consultar, después de obtener respuesta:
await otorgar_puntos(
    db,
    current_user.id,
    5,
    "coach_consulta",
    "Consulta al Coach IA"
)

# En telegram_webhook.handle_message, después de guardar respuesta:
await otorgar_puntos(
    db_instance,
    user['id'],
    10,
    "respuesta_lmv",
    f"Respuesta a pregunta {tipo}"
)
```

#### **Paso 3: Agregar leaderboard al Dashboard** (5 min)

Actualizar `/app/frontend/src/pages/DashboardPage.js`:

```javascript
const [leaderboard, setLeaderboard] = useState([]);

useEffect(() => {
  const fetchLeaderboard = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/leaderboard`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  fetchLeaderboard();
}, []);

// En el JSX:
<Card className="bg-[#1A2F47] border-[#2D3748]">
  <CardHeader>
    <CardTitle className="text-white">🏆 Tabla de Líderes</CardTitle>
  </CardHeader>
  <CardContent>
    <div className="space-y-2">
      {leaderboard.slice(0, 10).map((user, index) => (
        <div key={index} className="flex items-center justify-between p-2 bg-slate-800 rounded">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{index + 1}°</span>
            <div>
              <p className="text-white font-semibold">{user.nombre} {user.apellido}</p>
              <p className="text-gray-400 text-sm">Nivel {user.nivel}</p>
            </div>
          </div>
          <div className="text-green-400 font-bold">{user.puntos_totales} pts</div>
        </div>
      ))}
    </div>
  </CardContent>
</Card>
```

---

## ✅ TESTING COMPLETO

### **1. Test Telegram:**
```
1. Abrir Telegram
2. Buscar @Evoll_Orenes_Bot
3. Enviar /start
4. Copiar código EVOLL-XXXXX
5. Ir a Perfil en web
6. Vincular con código
7. Click "Enviar Prueba"
8. Verificar notificación en Telegram
```

### **2. Test Coach IA:**
```
1. Ir a Coach IA
2. Enviar mensaje de texto → verificar respuesta en markdown
3. Grabar audio → verificar transcripción + respuesta
4. Verificar que se otorgaron puntos
```

### **3. Test Notificaciones L-M-V:**
```bash
# Ejecutar manualmente
cd /app/backend
python cron_notificaciones.py

# Verificar que se envió a Telegram
# Responder en Telegram
# Verificar que se guardó respuesta y se otorgaron puntos
```

### **4. Test VAPI:**
```
1. Ir a Coach IA
2. Ingresar número de teléfono
3. Click "Llamar"
4. Verificar que llega llamada
5. Probar conversación de voz
```

---

## 🔧 TROUBLESHOOTING

### **Problema: Telegram no envía mensajes**
```bash
# Verificar logs
tail -f /var/log/supervisor/backend.err.log

# Verificar token
grep TELEGRAM_BOT_TOKEN /app/backend/.env

# Test manual
cd /app/backend
python -c "
from telegram_bot import telegram_notifier
import asyncio
asyncio.run(telegram_notifier.verificar_bot())
"
```

### **Problema: VAPI no inicia llamadas**
```bash
# Verificar configuración
grep VAPI /app/backend/.env

# Test manual
cd /app/backend
python -c "
from vapi_integration import iniciar_llamada_vapi
import asyncio
result = asyncio.run(iniciar_llamada_vapi('+34612345678', {'nombre': 'Test'}))
print(result)
"
```

---

FIN DE LA GUÍA RÁPIDA
