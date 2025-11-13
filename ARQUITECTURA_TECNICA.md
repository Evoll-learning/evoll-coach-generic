# 🏗️ ARQUITECTURA TÉCNICA - EVOLL LIDERAZGO

---

## 📐 DIAGRAMA DE ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│                    Port 3000 (Nginx → 80/443)                   │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Landing  │  │Dashboard │  │ Coach IA │  │  Perfil  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│       │              │              │              │            │
│       └──────────────┴──────────────┴──────────────┘            │
│                          │                                      │
│                   AuthContext + API calls                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTPS/REST API
                           │ All routes prefixed with /api
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│                        Port 8001                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API ROUTES (/api)                      │  │
│  │                                                            │  │
│  │  /auth/register    /auth/login                            │  │
│  │  /coach/consultar  /coach/audio                           │  │
│  │  /telegram/*       /vapi/* (pendiente)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│              ┌───────────┴───────────┐                          │
│              │                       │                          │
│              ▼                       ▼                          │
│    ┌──────────────────┐    ┌──────────────────┐               │
│    │ MongoDB (Local)  │    │ Supabase Client  │               │
│    │ Temporal/Fallback│    │ Future Primary   │               │
│    └──────────────────┘    └──────────────────┘               │
│              │                       │                          │
│              │                       │                          │
│    ┌─────────▼────────────────────────▼───────────┐            │
│    │         Integration Modules                   │            │
│    │                                               │            │
│    │  • coach_ia_integration.py                    │            │
│    │    - GPT-4o (emergentintegrations)           │            │
│    │    - Whisper (audio transcription)           │            │
│    │                                               │            │
│    │  • telegram_webhook.py                        │            │
│    │    - Message handlers                         │            │
│    │    - Command processors                       │            │
│    │                                               │            │
│    │  • telegram_bot.py                            │            │
│    │    - Notification sender                      │            │
│    └───────────────────────────────────────────────┘            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
        ┌──────────────┐    ┌──────────────┐
        │   TELEGRAM   │    │  EMERGENT    │
        │     BOT      │    │     LLM      │
        │@Evoll_Orenes │    │   GPT-4o +   │
        │    _Bot      │    │   Whisper    │
        └──────────────┘    └──────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                           │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Supabase │  │ Telegram │  │Emergent  │  │   VAPI   │       │
│  │PostgreSQL│  │   API    │  │   LLM    │  │ (pending)│       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 FLUJOS DE DATOS PRINCIPALES

### **1. Registro y Login de Usuario**

```
User → Frontend (Form) → Backend /api/auth/register
                              │
                              ├─→ Hash password (bcrypt)
                              ├─→ Insert into MongoDB/Supabase
                              ├─→ Generate JWT token
                              └─→ Return token

User → Frontend (Login) → Backend /api/auth/login
                              │
                              ├─→ Verify credentials
                              ├─→ Generate JWT token
                              └─→ Return token + user data

Frontend stores token → All API calls include: Authorization: Bearer {token}
```

---

### **2. Vinculación de Telegram**

```
User → Telegram App → @Evoll_Orenes_Bot
                          │
                          ├─→ User sends: /start
                          │
                          ├─→ Bot generates code: EVOLL-{chat_id}
                          │
                          └─→ Bot sends code to user

User → Frontend (Perfil) → Paste code: EVOLL-123456789
                              │
                              ├─→ Backend /api/telegram/vincular
                              │
                              ├─→ Extract chat_id from code
                              │
                              ├─→ Update user.telegram_chat_id in DB
                              │
                              └─→ Send confirmation via Telegram

✅ User is now linked and can receive notifications
```

---

### **3. Coach IA - Consulta de Texto**

```
User → Frontend (CoachIAPage) → Type message
                                    │
                                    ├─→ POST /api/coach/consultar
                                    │   Body: { mensaje: "..." }
                                    │
Backend receives request              │
    │                                 │
    ├─→ Get user context from token  │
    ├─→ Build system prompt          │
    ├─→ Call GPT-4o via emergent LLM │
    │   (coach_ia_integration.py)    │
    │                                 │
    └─→ Return formatted response     │
                                      │
Frontend receives response            │
    │                                 │
    └─→ Render with ReactMarkdown     │
        (bullet points, bold, etc)    │
```

---

### **4. Coach IA - Consulta de Audio**

```
User → Frontend → Press microphone button 🎤
                    │
                    ├─→ Request mic permission
                    ├─→ Start MediaRecorder
                    ├─→ Record audio (webm format)
                    └─→ Press stop button 🔴

Audio recorded → POST /api/coach/audio (FormData)
                    │
Backend receives audio file
    │
    ├─→ Save to temp file
    ├─→ Transcribe with Whisper API
    │   (emergentintegrations)
    ├─→ Get text transcription
    ├─→ Delete temp file
    ├─→ Send transcription to GPT-4o
    │   (same as text flow)
    └─→ Return:
        {
          transcripcion: "...",
          respuesta: "..."
        }

Frontend receives response
    │
    └─→ Display: 🎤 [transcription]
        + AI response with markdown
```

---

### **5. Notificaciones Automáticas L-M-V** (Pendiente implementar)

```
CRON JOB (Daily 9:00 AM)
    │
    ├─→ Check day of week
    │   - Monday    → Liderazgo
    │   - Wednesday → Management
    │   - Friday    → Valores
    │
    ├─→ Select question from preguntas_lmv_completas.py
    │   Based on: current week + tipo
    │
    ├─→ Query all users with telegram_chat_id != null
    │   AND notificaciones_activas = true
    │
    ├─→ For each user:
    │   │
    │   ├─→ Send question via Telegram
    │   │   (telegram_bot.notificar_pregunta_dia)
    │   │
    │   └─→ Insert record in respuestas_lmv
    │       (pregunta sent, respuesta = null)
    │
    └─→ Log results

User receives notification in Telegram
    │
    └─→ User replies with text

Telegram → telegram_webhook.handle_message
    │
    ├─→ Find user by chat_id
    ├─→ Find pending respuesta_lmv
    ├─→ Update respuesta field
    ├─→ Award points (+10)
    └─→ Send confirmation to user
```

---

### **6. VAPI - Llamadas de Voz** (Pendiente implementar)

```
User → Frontend (CoachIAPage) → Click "📞 Llamar a mi Coach"
                                    │
                                    ├─→ POST /api/coach/iniciar-llamada
                                    │
Backend receives request              │
    │                                 │
    ├─→ Call VAPI API                │
    │   with assistant_id             │
    │   and user phone number          │
    │                                 │
    └─→ Return call_id                │
                                      │
VAPI initiates call                   │
    │                                 │
    ├─→ User's phone rings           │
    ├─→ User answers                  │
    └─→ Voice conversation with AI    │
        Coach in real-time            │

Call ends → VAPI webhook → /api/vapi/webhook
    │
    ├─→ Receive call transcript
    ├─→ Save in conversaciones_coach
    └─→ Award points
```

---

## 💾 MODELO DE DATOS

### **MongoDB (Current):**

```javascript
// Collection: users
{
  _id: ObjectId,
  id: "uuid",
  email: "user@example.com",
  password_hash: "bcrypt_hash",
  nombre: "Juan",
  apellido: "Pérez",
  cargo: "Manager",
  division: "Ventas",
  telegram_chat_id: "123456789",
  notificaciones_activas: true,
  created_at: ISODate,
  onboarding_completed: true
}
```

### **Supabase PostgreSQL (Future Primary):**

```sql
-- Table: users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE,
    nombre TEXT,
    apellido TEXT,
    cargo TEXT,
    division TEXT,
    telegram_chat_id TEXT,
    notificaciones_activas BOOLEAN,
    puntos_totales INTEGER,
    nivel INTEGER,
    racha_dias INTEGER,
    auth_user_id UUID REFERENCES auth.users(id)
);

-- Table: respuestas_lmv
CREATE TABLE respuestas_lmv (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    semana INTEGER,
    tipo TEXT, -- 'Liderazgo', 'Management', 'Valores'
    pregunta TEXT,
    respuesta TEXT,
    fecha_respuesta TIMESTAMPTZ,
    puntos_otorgados INTEGER
);

-- Table: badges
CREATE TABLE badges (
    id UUID PRIMARY KEY,
    codigo TEXT UNIQUE,
    nombre TEXT,
    descripcion TEXT,
    icono TEXT,
    puntos_requeridos INTEGER
);

-- Table: user_badges
CREATE TABLE user_badges (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    badge_id UUID REFERENCES badges(id),
    obtenido_en TIMESTAMPTZ
);
```

---

## 🔐 SEGURIDAD Y AUTENTICACIÓN

### **Current: Custom JWT Authentication**

```
1. User registers/logins
2. Backend generates JWT token:
   - Payload: { email, user_id, exp }
   - Signed with SECRET_KEY
   - Expires in 30 days

3. Frontend stores token in localStorage

4. All API calls include:
   Authorization: Bearer {token}

5. Backend verifies token on each request:
   - Decode with SECRET_KEY
   - Check expiration
   - Extract user_id
   - Get user from DB
```

### **Future: Supabase Auth**

```
1. User registers via Supabase Auth
2. Supabase handles password hashing, JWT, etc
3. Frontend uses supabase.auth.signUp()
4. Token is managed by Supabase client
5. RLS policies protect data automatically
```

---

## 🔌 INTEGRACIONES EXTERNAS

### **1. Emergent LLM (OpenAI)**
```python
from emergentintegrations.llm.chat import LlmChat
from emergentintegrations.llm.openai import OpenAISpeechToText

# Text generation
llm = LlmChat(api_key=EMERGENT_LLM_KEY, model="gpt-4o")
response = await llm.chat([UserMessage(content="...")])

# Audio transcription
stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
transcription = await stt.transcribe(file=audio_file, model="whisper-1")
```

**Ventajas:**
- Una sola key para múltiples modelos
- Budget compartido
- Sin necesidad de OpenAI API key propia

---

### **2. Telegram Bot API**
```python
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler

# Initialize bot
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Send message
bot = Bot(token=TELEGRAM_BOT_TOKEN)
await bot.send_message(chat_id=chat_id, text="Hello!")

# Handle incoming messages
async def handle_message(update: Update, context):
    text = update.message.text
    # Process...
```

**Endpoints usados:**
- `sendMessage` - Enviar notificaciones
- `getUpdates` - Recibir mensajes (polling mode)

---

### **3. VAPI (Pendiente)**
```python
import httpx

# Iniciar llamada
async with httpx.AsyncClient() as client:
    response = await client.post(
        "https://api.vapi.ai/call",
        headers={"Authorization": f"Bearer {VAPI_API_KEY}"},
        json={
            "assistant_id": ASSISTANT_ID,
            "phone_number": user_phone,
            "metadata": {...}
        }
    )
```

---

## 🚀 DEPLOYMENT

### **Current Environment:**
- Kubernetes container
- Supervisor manages processes
- Nginx reverse proxy

### **Services:**
```
backend         RUNNING   pid 765
frontend        RUNNING   pid 123
mongodb         RUNNING   pid 456
nginx-proxy     RUNNING   pid 789
```

### **URLs:**
- Preview: https://coach-ai-9.preview.emergentagent.com
- Backend: https://coach-ai-9.preview.emergentagent.com/api
- Frontend: https://coach-ai-9.preview.emergentagent.com/

---

## 📊 RENDIMIENTO Y ESCALABILIDAD

### **Current Bottlenecks:**
- MongoDB local (single instance)
- No caching layer
- Synchronous Telegram bot (polling)

### **Future Improvements:**
- Migrate to Supabase (distributed PostgreSQL)
- Add Redis for caching
- Webhook mode for Telegram (faster)
- Background job queue (Celery/RQ)

---

## 🧪 TESTING

### **Manual Testing:**
```bash
# Backend health
curl https://[url]/api/health

# Auth
curl -X POST https://[url]/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123",...}'

# Coach IA
curl -X POST https://[url]/api/coach/consultar \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"mensaje":"¿Cómo mejorar mi liderazgo?"}'
```

### **Automated Testing:** (Pendiente)
- Unit tests con pytest
- Integration tests con TestClient
- E2E tests con Playwright

---

## 📝 LOGS Y DEBUGGING

### **Log Locations:**
```bash
/var/log/supervisor/backend.err.log
/var/log/supervisor/backend.out.log
/var/log/supervisor/frontend.err.log
/var/log/supervisor/frontend.out.log
```

### **Common Commands:**
```bash
# Tail logs
tail -f /var/log/supervisor/backend.err.log

# Search for errors
grep -i error /var/log/supervisor/backend.err.log

# Check last 50 lines
tail -n 50 /var/log/supervisor/backend.err.log
```

---

FIN DEL DOCUMENTO DE ARQUITECTURA
