# 📘 DOCUMENTACIÓN TÉCNICA - PLATAFORMA EvoLL

## Grupo Orenes - Programa de Liderazgo Evolutivo

**Versión:** 1.0  
**Fecha:** Noviembre 2025  
**Escala:** 350 managers  

---

## 🏗️ ARQUITECTURA GENERAL

### Stack Tecnológico

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND                             │
│  React 19 + Tailwind CSS + Shadcn UI + Recharts        │
│  Gestión de Estado: Context API + Axios                │
└─────────────────┬───────────────────────────────────────┘
                  │ REST API
┌─────────────────┴───────────────────────────────────────┐
│                     BACKEND                              │
│  FastAPI (Python) + Pydantic + JWT Auth                │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────────┐
│                    DATABASE                              │
│  MongoDB 6.x (NoSQL) - Motor AsyncIO                    │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
/app
├── backend/
│   ├── server.py                 # API principal FastAPI
│   ├── requirements.txt          # Dependencias Python
│   └── .env                      # Variables de entorno
│
├── frontend/
│   ├── src/
│   │   ├── pages/               # Páginas principales
│   │   │   ├── LandingPage.js
│   │   │   ├── OnboardingPage.js
│   │   │   ├── DashboardPage.js
│   │   │   ├── ComunidadPage.js
│   │   │   ├── CoachIAPage.js
│   │   │   └── PerfilPage.js
│   │   │
│   │   ├── components/
│   │   │   ├── ui/              # Shadcn UI components
│   │   │   └── DashboardCharts.js  # Gráficas personalizadas
│   │   │
│   │   ├── context/
│   │   │   └── AuthContext.js   # Gestión de autenticación
│   │   │
│   │   ├── App.js               # Componente principal
│   │   └── App.css              # Estilos globales (verde Orenes)
│   │
│   ├── package.json
│   └── .env
│
├── NEXT_STEPS.md
├── ARQUITECTURA_TECNICA_EVOLL.md (este archivo)
└── README.md
```

---

## 🎨 IDENTIDAD VISUAL - COLORES ORENES

### Paleta de Colores Principal

```css
/* Verde Corporativo Orenes */
--orenes-green-primary: #2D9B4E;    /* Verde principal */
--orenes-green-dark: #1B5E32;       /* Verde oscuro */
--orenes-green-light: #3DB35F;      /* Verde claro */
--orenes-green-lighter: #4FD670;    /* Verde más claro */

/* Acento */
--orenes-accent-gold: #F59E0B;      /* Dorado para detalles */

/* Dark Theme (Dashboard) */
--dark-bg-primary: #0A1628;         /* Fondo oscuro principal */
--dark-bg-secondary: #132337;       /* Fondo oscuro secundario */
--dark-bg-card: #1A2F47;           /* Fondo de tarjetas */
--dark-text-primary: #E5E7EB;       /* Texto claro */
--dark-text-secondary: #9CA3AF;     /* Texto gris */
--dark-border: #2D3748;             /* Bordes */
```

### Tipografía

- **Headings:** Space Grotesk (600-700)
- **Body:** Inter (400-500)
- **Números/Métricas:** Space Grotesk Bold

### Componentes Visuales

**Dashboard Moderno:**
- Gráfica circular de progreso (Circular Progress)
- Barras horizontales con gradiente verde
- Cards con efecto hover y borde superior verde
- Dark theme con contraste alto

---

## 🔐 AUTENTICACIÓN Y SEGURIDAD

### Sistema de Autenticación

**Tipo:** JWT (JSON Web Tokens)

**Flujo:**
```
1. Usuario → Registro/Login
2. Backend → Valida credenciales
3. Backend → Genera JWT (válido 30 días)
4. Frontend → Guarda token en localStorage
5. Todas las requests → Header: Authorization: Bearer {token}
```

**Implementación:**

```python
# Backend - server.py
SECRET_KEY = "evoll-orenes-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Password hashing con bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

**Protección de Rutas:**
- Frontend: `PrivateRoute` component con Context API
- Backend: Dependency `get_current_user()`

---

## 💾 BASE DE DATOS - MONGODB

### Colecciones

#### 1. **users**
```javascript
{
  id: String (UUID),
  email: EmailStr,
  hashed_password: String,
  nombre: String,
  apellido: String,
  cargo: String,
  division: String, // "operaciones", "ventas", "rrhh", etc.
  experiencia_anos: Int,
  tamano_equipo: Int,
  desafios_equipo: String,
  objetivos_personales: String,
  valores_compromiso: String,
  fecha_registro: DateTime,
  onboarding_completado: Boolean,
  semana_actual: Int (1-48),
  bloque_actual: Int (1-5)
}
```

#### 2. **respuestas_lmv**
```javascript
{
  id: String (UUID),
  user_id: String,
  semana: Int,
  bloque: Int,
  numero_envio: String, // "P1", "P2", "P3"
  pregunta: String,
  respuesta_texto: String,
  respuesta_audio_url: String (opcional),
  feedback_ia: String (opcional),
  puntuacion: Int (opcional),
  fecha_respuesta: DateTime
}
```

#### 3. **evaluaciones_mensuales**
```javascript
{
  id: String (UUID),
  user_id: String,
  mes: Int,
  bloque: Int,
  metricas: {
    comunicacion_efectiva: Int,
    feedback_constructivo: Int,
    gestion_conflictos: Int,
    delegacion: Int,
    inteligencia_emocional: Int,
    pensamiento_estrategico: Int
  },
  resumen_ia: String,
  recomendaciones: [String],
  fecha_evaluacion: DateTime
}
```

#### 4. **posts_comunidad**
```javascript
{
  id: String (UUID),
  user_id: String,
  autor_nombre: String,
  contenido: String,
  tags: [String], // ["#feedback", "#motivación", etc.]
  likes: Int,
  comentarios: Int,
  fecha_creacion: DateTime
}
```

---

## 🔌 API REST - ENDPOINTS

### Base URL
```
Production: https://coach-ai-9.preview.emergentagent.com/api
```

### Endpoints Principales

#### Autenticación
```
POST   /api/auth/register       # Registro de usuario
POST   /api/auth/login          # Login
GET    /api/auth/me             # Obtener usuario actual
PUT    /api/auth/onboarding     # Completar onboarding
```

#### Sistema L-M-V
```
GET    /api/lmv/pregunta-dia    # Obtener pregunta del día
POST   /api/lmv/responder       # Enviar respuesta
GET    /api/lmv/mis-respuestas  # Historial de respuestas
```

#### Métricas
```
GET    /api/metricas/progreso   # Métricas de progreso del usuario
```

#### Comunidad
```
GET    /api/comunidad/posts     # Obtener posts (paginated)
POST   /api/comunidad/posts     # Crear nuevo post
```

#### Coach IA
```
POST   /api/coach/consultar     # Consultar al coach IA
```

### Ejemplo de Request

```bash
# Login
curl -X POST https://coach-ai-9.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "carlos.rodriguez@orenes.com",
    "password": "password123"
  }'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "carlos.rodriguez@orenes.com",
    "nombre": "Carlos",
    ...
  }
}
```

---

## 📊 SISTEMA L-M-V (Lunes-Miércoles-Viernes)

### Funcionamiento

**Estructura:**
- 48 semanas de programa
- 3 preguntas por semana (Lunes, Miércoles, Viernes)
- Total: 144 preguntas

**Lógica:**
```python
# Backend determina día de la semana
dia_semana = datetime.now(timezone.utc).weekday()

if dia_semana == 0:  # Lunes
    numero_envio = "P1"
elif dia_semana == 2:  # Miércoles
    numero_envio = "P2"
elif dia_semana == 4:  # Viernes
    numero_envio = "P3"
else:
    return "No hay pregunta hoy"
```

**Tipos de Preguntas:**
- **Reflexiva:** Autoexploración y valores
- **Análisis:** Casos prácticos y situaciones
- **Aplicación:** Práctica y acción concreta
- **Introspección:** Emociones y autoconciencia

---

## 🎯 MÉTRICAS DE LIDERAZGO

### Competencias Evaluadas

1. **Comunicación Efectiva**
   - Claridad en el mensaje
   - Escucha activa
   - Adaptación al interlocutor

2. **Feedback Constructivo** ⭐ PRIORIDAD ORENES
   - Feedback hacia arriba (jefes)
   - Feedback hacia abajo (subordinados)
   - Manejo de feedback negativo

3. **Gestión de Conflictos**
   - Identificación temprana
   - Mediación efectiva
   - Resolución win-win

4. **Delegación**
   - Confianza en el equipo
   - Seguimiento apropiado
   - Empoderamiento

5. **Inteligencia Emocional**
   - Autoconciencia
   - Autorregulación
   - Empatía

6. **Pensamiento Estratégico**
   - Visión a largo plazo
   - Toma de decisiones
   - Priorización

### Cálculo de Métricas

**Actual:** Simulado con valores base
**Futuro:** Calculado con IA analizando respuestas

```python
# Pseudocódigo futuro
def calcular_metrica(user_id, competencia):
    respuestas = obtener_respuestas_relacionadas(user_id, competencia)
    analisis_ia = gpt4o.analizar(respuestas)
    return analisis_ia.score  # 0-100
```

---

## 🤖 COACH IA - ARQUITECTURA FUTURA

### Fase Actual: Simulado
```python
@api_router.post("/coach/consultar")
async def consultar_coach(request: CoachIARequest):
    # Respuesta simulada
    return {"respuesta": "Gracias por tu consulta..."}
```

### Fase 2: Integración Real con GPT-4o

**Recomendación:** OpenAI GPT-4o con Clave Universal Emergent

**Implementación sugerida:**
```python
import openai

@api_router.post("/coach/consultar")
async def consultar_coach(request: CoachIARequest, user: User = Depends(get_current_user)):
    # Contexto personalizado
    contexto = f"""
    Eres un coach de liderazgo experto trabajando con {user.nombre},
    {user.cargo} en {user.division} de Grupo Orenes.
    
    Desafíos del equipo: {user.desafios_equipo}
    Objetivos: {user.objetivos_personales}
    
    Valores Orenes: Experiencia, Confianza, Compromiso, Sentimiento Familiar
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": contexto},
            {"role": "user", "content": request.mensaje}
        ],
        temperature=0.7
    )
    
    return {"respuesta": response.choices[0].message.content}
```

**Costo estimado:** $50-100/mes para 350 usuarios con clave universal

---

## 📱 SISTEMA DE NOTIFICACIONES (PRÓXIMO)

### Arquitectura Propuesta

```
┌──────────────┐       ┌──────────┐       ┌─────────────┐       ┌──────────────┐
│  MongoDB     │──────▶│  n8n     │──────▶│ Twilio API  │──────▶│  WhatsApp    │
│  Trigger     │       │ Workflow │       │             │       │  Usuario     │
└──────────────┘       └──────────┘       └─────────────┘       └──────────────┘
```

### Opciones de Mensajería

#### Opción A: WATI.io (Recomendado)
- **Pros:** Fácil, económico ($49/mes), interfaz amigable
- **Contras:** Límite de mensajes/día
- **Ideal para:** Piloto y primeras 100 usuarios

#### Opción B: Twilio (Escalable)
- **Pros:** Robusto, sin límites, API completa
- **Costo:** $0.005/mensaje WhatsApp
- **Ideal para:** 350+ usuarios

#### Opción C: Telegram Bot (Alternativa)
- **Pros:** Gratis, fácil integración, bots poderosos
- **Contras:** Menos adopción que WhatsApp en España
- **Ideal para:** Piloto técnico

### Flujo de Notificaciones

```javascript
// n8n Workflow
1. Cron Trigger (L-M-V 9:00 AM)
2. MongoDB Query (usuarios activos)
3. For Each Usuario:
   - Generar link personalizado
   - Enviar WhatsApp: "¡Nueva pregunta EvoLL! 🎯 [Link]"
4. Registrar envío en DB
```

---

## 🔗 INTEGRACIÓN CON SUPABASE (Tu plataforma)

### Opción 1: API REST

**Endpoints para crear en EvoLL:**
```
# SSO - Single Sign-On
POST /api/sso/token
- Input: Supabase JWT
- Output: EvoLL JWT

# Sincronización de datos
GET  /api/users/{id}/dashboard
POST /api/webhooks/supabase
```

**En tu plataforma Supabase:**
```javascript
// Función Edge (Supabase)
const response = await fetch('https://evoll-api.com/api/sso/token', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${supabaseJWT}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ user_id: userId })
});

const evollToken = await response.json();
// Redirigir a EvoLL con token
window.location.href = `https://evoll.com?token=${evollToken.access_token}`;
```

### Opción 2: Iframe Embedded

```html
<!-- En tu plataforma Supabase -->
<iframe 
  src="https://coach-ai-9.preview.emergentagent.com?embedded=true&token={JWT}"
  width="100%" 
  height="800px"
  frameborder="0"
></iframe>
```

### Opción 3: Webhooks Bidireccionales

**EvoLL → Supabase:**
```python
# Cuando usuario completa evaluación mensual
await httpx.post(
    'https://tu-supabase-url.com/webhooks/evoll',
    json={
        'event': 'evaluation_completed',
        'user_id': user.id,
        'data': evaluation
    },
    headers={'Authorization': f'Bearer {WEBHOOK_SECRET}'}
)
```

---

## 🎮 GAMIFICACIÓN (Próxima Fase)

### Sistema de Puntos

```javascript
{
  // Acciones y puntos
  responder_lmv: 10,
  racha_3_dias: 50,
  racha_semana_completa: 100,
  publicar_comunidad: 15,
  recibir_like: 5,
  consultar_coach: 5,
  
  // Badges
  badges: {
    consistente: "4 semanas sin fallar",
    reflexivo: "50 respuestas profundas",
    comunicador: "20 posts en comunidad",
    mentor: "Ayudaste a 5 compañeros"
  }
}
```

### Leaderboard

**Colecciones adicionales:**
```javascript
// gamification_scores
{
  user_id: String,
  puntos_totales: Int,
  nivel: Int,
  badges: [String],
  racha_actual: Int,
  racha_maxima: Int,
  posicion_division: Int,
  posicion_global: Int
}
```

---

## 📈 PANEL CORPORATIVO RRHH

### Vista Agregada (Sin datos privados)

**Métricas disponibles:**
```javascript
// Dashboard RRHH
{
  global: {
    usuarios_activos: 320,
    tasa_participacion: 91.4%,
    promedio_respuestas_semana: 2.7,
    tiempo_promedio_plataforma: "12min/semana"
  },
  
  por_division: {
    operaciones: {
      participacion: 85%,
      mejora_comunicacion: +15%
    },
    ventas: {
      participacion: 92%,
      mejora_feedback: +22%
    }
  },
  
  competencias_agregadas: {
    comunicacion: 74%,  // Promedio global
    feedback: 68%,
    gestion_conflictos: 71%
  },
  
  alertas: [
    "5 usuarios inactivos >2 semanas",
    "División Finanzas: participación baja (65%)"
  ]
}
```

### Reportes Automáticos

**PDF Mensual Ejecutivo:**
- Participación global
- Tendencias por división
- Mejoras en competencias
- Recomendaciones

---

## ⚙️ CONFIGURACIÓN Y DEPLOYMENT

### Variables de Entorno

**Backend (.env):**
```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=evoll_orenes
CORS_ORIGINS=*
JWT_SECRET_KEY=evoll-orenes-secret-key-change-in-production

# Futuro
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
N8N_WEBHOOK_URL=...
```

**Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=https://coach-ai-9.preview.emergentagent.com
```

### Comandos Útiles

```bash
# Backend
cd /app/backend
pip install -r requirements.txt
sudo supervisorctl restart backend

# Frontend
cd /app/frontend
yarn install
yarn start
sudo supervisorctl restart frontend

# Logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## 🧪 TESTING

### Test de Usuario Completo

```bash
# 1. Crear usuario
curl -X POST https://coach-ai-9.preview.emergentagent.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@orenes.com","password":"pass123","nombre":"Test","apellido":"User"}'

# 2. Login
curl -X POST https://coach-ai-9.preview.emergentagent.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@orenes.com","password":"pass123"}'

# 3. Obtener pregunta del día
curl -X GET https://coach-ai-9.preview.emergentagent.com/api/lmv/pregunta-dia \
  -H "Authorization: Bearer {TOKEN}"

# 4. Responder
curl -X POST https://coach-ai-9.preview.emergentagent.com/api/lmv/responder \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"pregunta":"...","respuesta_texto":"Mi reflexión..."}'
```

---

## 📊 MÉTRICAS DE RENDIMIENTO

### Objetivos de Performance

- **Carga de dashboard:** < 2 segundos
- **API response time:** < 500ms (p95)
- **Uptime:** > 99.5%
- **Concurrent users:** 350+

### Monitoreo

**Herramientas sugeridas:**
- Uptime: UptimeRobot o Pingdom
- Performance: Google Analytics 4
- Errors: Sentry
- API Monitoring: Postman Monitor

---

## 🔄 ROADMAP DE DESARROLLO

### Fase 1 - COMPLETADO ✅
- [x] Identidad visual verde Orenes
- [x] Dashboard dark theme moderno
- [x] Sistema L-M-V básico (semanas 1-2)
- [x] Autenticación JWT
- [x] Onboarding completo
- [x] Comunidad básica

### Fase 2 - EN PROGRESO 🚧
- [ ] Integración Coach IA (GPT-4o)
- [ ] Sistema notificaciones WhatsApp
- [ ] Completar 144 preguntas L-M-V
- [ ] Panel RRHH básico

### Fase 3 - PRÓXIMAMENTE 📅
- [ ] Gamificación completa
- [ ] Evaluaciones mensuales automáticas
- [ ] Feedback Simulator con IA
- [ ] Integración con plataforma Supabase
- [ ] Mobile app (React Native)

---

## 📞 SOPORTE TÉCNICO

### Para Desarrolladores

**Acceso a la plataforma:**
- URL: https://coach-ai-9.preview.emergentagent.com
- Usuarios de prueba:
  - `carlos.rodriguez@orenes.com` / `password123`
  - `maria.gonzalez@orenes.com` / `password123`

**Documentación adicional:**
- API Docs: `/api/docs` (FastAPI auto-generated)
- GitHub: [Si aplicable]

### Explicar a Profesionales Externos

**Si necesitas contratar desarrollador:**

1. **Stack:** "Es una app web React + Python con MongoDB"
2. **APIs:** "Necesitamos integrar OpenAI GPT-4o para el coach IA"
3. **Notificaciones:** "Implementar WhatsApp con Twilio o WATI.io"
4. **Escala:** "Debe soportar 350 usuarios concurrentes"

**Habilidades requeridas:**
- React.js (hooks, context API)
- Python FastAPI
- MongoDB (experiencia con NoSQL)
- REST APIs
- Integración de servicios terceros (OpenAI, Twilio)

---

## 💡 PREGUNTAS FRECUENTES

**Q: ¿Cómo añado más preguntas L-M-V?**  
A: Edita `PREGUNTAS_LMV` en `/app/backend/server.py`

**Q: ¿Cómo cambio los colores?**  
A: Modifica las CSS variables en `/app/frontend/src/App.css`

**Q: ¿Cómo conecto con mi Supabase?**  
A: Ver sección "Integración con Supabase" de este documento

**Q: ¿Puedo desplegar en mi propio servidor?**  
A: Sí, necesitas:
- Docker o Python + Node.js
- MongoDB
- Variables de entorno configuradas

**Q: ¿Cuánto cuesta mantener esto?**  
A: ~$100-150/mes para 350 usuarios:
- Hosting: $50
- MongoDB: $10
- Coach IA: $50-100
- WhatsApp: $50

---

## 📄 LICENCIA Y PROPIEDAD

**Propiedad:** Grupo Orenes  
**Desarrollado por:** Emergent Agent (E1)  
**Fecha:** Noviembre 2025  

---

**Documento vivo - Se actualizará con cada nueva fase**

Para más información técnica o consultas específicas, contacta al equipo de desarrollo.
