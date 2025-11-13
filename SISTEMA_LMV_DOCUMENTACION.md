# 📚 SISTEMA L-M-V (LIDERAZGO-MANAGEMENT-VALORES)
## Documentación Completa del Sistema de Preguntas Automáticas

**Fecha**: Noviembre 2025  
**Estado**: MVP - Sistema preparado pero NO activado  
**Para activar**: Ver sección "Activación" al final

---

## 🎯 **¿QUÉ ES EL SISTEMA L-M-V?**

Sistema automático que envía **3 preguntas semanales** (Lunes, Miércoles, Viernes) vía **Telegram** a cada líder del programa EvoLL de Grupo Orenes.

**Objetivo**: 
- Reflexión continua sobre liderazgo
- Desarrollo de competencias clave
- Engagement constante con el programa
- Gamificación (puntos por responder)

---

## 📅 **CÓMO FUNCIONA (CUANDO ESTÉ ACTIVO)**

### **Flujo Automático:**

```
┌─────────────────────────────────────────────────────┐
│  LUNES 9:00 AM                                      │
│  ├─ Cron job se ejecuta automáticamente             │
│  ├─ Selecciona pregunta de la semana actual         │
│  ├─ Envía a TODOS los usuarios con Telegram activo  │
│  └─ Notificación llega a Telegram                   │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  USUARIO RECIBE EN TELEGRAM                         │
│  ├─ Pregunta de reflexión                           │
│  ├─ Link al Dashboard                               │
│  └─ Tiempo estimado: 2-3 minutos                    │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  USUARIO PUEDE RESPONDER:                           │
│  ├─ Opción A: Directamente en Telegram (texto)      │
│  ├─ Opción B: Desde Dashboard (texto o audio)       │
│  └─ El sistema registra la respuesta                │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  GAMIFICACIÓN AUTOMÁTICA                            │
│  ├─ +10 puntos por responder                        │
│  ├─ Actualiza racha (días consecutivos)             │
│  ├─ Actualiza leaderboard                           │
│  └─ Puede desbloquear badges                        │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  MIÉRCOLES 9:00 AM                                  │
│  └─ Se repite el proceso con nueva pregunta         │
└─────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│  VIERNES 9:00 AM                                    │
│  └─ Última pregunta de la semana                    │
└─────────────────────────────────────────────────────┘
```

---

## 📊 **ESTRUCTURA DE PREGUNTAS**

### **Banco de Preguntas:**
- **Total**: 144 preguntas (48 semanas x 3 preguntas)
- **Archivo**: `/app/backend/preguntas_lmv_completas.py`
- **Estructura por semana**:
  ```python
  {
    "semana": 1,
    "bloque": 1,
    "tema": "Autoconocimiento",
    "preguntas": [
      {
        "numero_envio": "P1",  # Lunes
        "tipo": "Reflexiva",
        "competencia": "Comunicación",
        "pregunta": "¿Cuál es tu mayor fortaleza como líder?"
      },
      {
        "numero_envio": "P2",  # Miércoles
        "tipo": "Práctica",
        "competencia": "Management",
        "pregunta": "¿Qué harías diferente en tu próxima reunión?"
      },
      {
        "numero_envio": "P3",  # Viernes
        "tipo": "Aplicada",
        "competencia": "Valores",
        "pregunta": "¿Cómo demuestras tus valores en decisiones difíciles?"
      }
    ]
  }
  ```

### **Tipos de Preguntas:**
1. **Reflexivas**: Autoconocimiento, introspección
2. **Prácticas**: Aplicación inmediata, situaciones reales
3. **Aplicadas**: Casos específicos, decisiones

### **Competencias Cubiertas:**
- Comunicación efectiva
- Gestión de conflictos
- Dar y recibir feedback
- Inteligencia emocional
- Delegación y empoderamiento
- Toma de decisiones
- Gestión del tiempo
- Liderazgo de equipos

---

## ⚙️ **COMPONENTES TÉCNICOS**

### **1. Cron Job**
**Archivo**: `/app/backend/cron_notificaciones.py`
**Función**: Ejecutar el endpoint `/api/cron/enviar-pregunta-dia` diariamente

**Configuración en servidor (cuando se active)**:
```bash
# Ejecutar a las 9:00 AM, Lunes, Miércoles y Viernes
0 9 * * 1,3,5 cd /app/backend && python cron_notificaciones.py >> /var/log/cron_lmv.log 2>&1
```

**Railway**: Usar Railway Cron Jobs o servicio externo como Cron-Job.org

### **2. Endpoint de Cron**
**Ruta**: `POST /api/cron/enviar-pregunta-dia`
**Ubicación**: `/app/backend/server.py` (línea ~850)

**Lógica**:
```python
1. Determinar qué día es (Lunes/Miércoles/Viernes)
2. Obtener semana actual del programa (contador global)
3. Buscar pregunta correspondiente en banco de preguntas
4. Obtener usuarios con Telegram activo
5. Para cada usuario:
   - Enviar notificación vía Telegram
   - Crear registro en respuestas_lmv (respuesta=null)
6. Retornar estadísticas (enviados, errores)
```

### **3. Bot de Telegram**
**Archivo**: `/app/backend/telegram_webhook.py`
**Bot**: `@Evoll_Orenes_Bot`

**Handlers**:
- `/start`: Genera código de vinculación
- `/estado`: Ver estado de vinculación
- **Mensajes de texto**: Captura respuestas a preguntas pendientes

**Lógica de captura de respuestas**:
```python
1. Usuario recibe pregunta en Telegram
2. Usuario responde con texto
3. Bot busca pregunta pendiente (respuesta=null) para ese user_id
4. Si encuentra:
   - Guarda respuesta
   - Otorga +10 puntos
   - Envía confirmación
5. Si no encuentra:
   - Guarda como mensaje general
```

### **4. Dashboard - Vista de Pregunta**
**Archivo**: `/app/frontend/src/pages/DashboardPage.js`
**Estado actual**: UI parcialmente implementada

**Funcionalidad cuando esté completa**:
- Card destacada con "Pregunta del Día"
- Botones: Responder por Texto / Responder por Audio
- Modal de respuesta
- Indicador de puntos ganados al responder

### **5. Base de Datos**

**Colección**: `respuestas_lmv`
```javascript
{
  id: "uuid",
  user_id: "uuid",
  semana: 1,
  bloque: 1,
  numero_envio: "P1",  // P1, P2, P3
  pregunta: "texto de la pregunta",
  respuesta: "respuesta del usuario" || null,
  fecha_envio: "2025-11-11T09:00:00Z",
  fecha_respuesta: "2025-11-11T14:30:00Z" || null,
  via: "telegram" || "dashboard",
  puntos_otorgados: 10,
  tipo: "Reflexiva",
  competencia: "Comunicación"
}
```

---

## 🎮 **GAMIFICACIÓN**

### **Sistema de Puntos:**
```javascript
PUNTOS_CONFIG = {
  'respuesta_lmv': 10,           // Por responder pregunta L-M-V
  'racha_7_dias': 50,            // Bonus por racha de 7 días
  'racha_30_dias': 200,          // Bonus por racha de 30 días
  'coach_consulta_texto': 5,     // Por usar Coach IA texto
  'coach_consulta_audio': 7      // Por usar Coach IA audio
}
```

### **Badges Disponibles:**
- 🔥 **Consistente**: 7 días de racha
- ⚡ **Imparable**: 30 días de racha
- 🎯 **Enfocado**: 10 respuestas L-M-V
- 🏆 **Maestro**: 50 respuestas L-M-V
- 💬 **Curioso**: 10 consultas al Coach
- 🎙️ **Comunicador**: 5 respuestas por audio

### **Leaderboard:**
**Endpoint**: `GET /api/leaderboard`
**Muestra**: Top 10 usuarios por puntos totales

---

## 📱 **EXPERIENCIA DE USUARIO (CUANDO ESTÉ ACTIVO)**

### **Lunes 9:00 AM:**
```
┌──────────────────────────────────────┐
│ 📱 TELEGRAM - @Evoll_Orenes_Bot      │
├──────────────────────────────────────┤
│ 🎯 ¡Nueva pregunta EvoLL!            │
│                                      │
│ 📅 Semana 1 • P1                     │
│ 🏷️ Tipo: Reflexiva                  │
│ 💡 Competencia: Comunicación         │
│                                      │
│ Pregunta:                            │
│ ¿Cuál es tu mayor fortaleza como     │
│ líder y cómo la demuestras a diario? │
│                                      │
│ 👉 Responder ahora                   │
│ (Link al Dashboard)                  │
│                                      │
│ Tiempo estimado: 2-3 minutos         │
└──────────────────────────────────────┘
```

### **Usuario responde directamente en Telegram:**
```
Usuario: "Mi mayor fortaleza es la empatía. 
La demuestro escuchando activamente a mi 
equipo en las 1-on-1 semanales."
```

### **Bot confirma:**
```
┌──────────────────────────────────────┐
│ ✅ ¡Respuesta guardada!              │
│                                      │
│ Has ganado +10 puntos 🎉             │
│                                      │
│ Gracias por tu reflexión sobre       │
│ liderazgo.                           │
│                                      │
│ Próxima pregunta: Miércoles 9:00 AM  │
└──────────────────────────────────────┘
```

### **O usuario va al Dashboard:**
```
┌─────────────────────────────────────────────┐
│ DASHBOARD                                   │
├─────────────────────────────────────────────┤
│ 🎯 Pregunta del Día (Lunes)                 │
│                                             │
│ ¿Cuál es tu mayor fortaleza como líder?    │
│                                             │
│ [Responder por Texto] [Responder por Audio] │
│                                             │
│ Ganarás +10 puntos 🎁                       │
└─────────────────────────────────────────────┘
```

---

## 📈 **MÉTRICAS Y ANALÍTICAS**

### **Endpoint de Métricas:**
`GET /api/metricas/progreso`

**Retorna**:
```javascript
{
  "participacion_lmv": {
    "respondidas": 12,
    "pendientes": 2,
    "porcentaje": 85.7
  },
  "racha_actual": 7,
  "racha_maxima": 14,
  "competencias": {
    "comunicacion": 78,     // % desarrollo
    "feedback": 65,
    "conflictos": 82,
    // ...
  }
}
```

---

## 🚀 **ACTIVACIÓN DEL SISTEMA**

### **ESTADO ACTUAL:**
- ❌ Cron job NO está activo
- ✅ Bot de Telegram funcionando
- ✅ Endpoint de envío implementado
- ✅ Banco de 144 preguntas listo
- ⏸️ UI del Dashboard parcial

### **PASOS PARA ACTIVAR:**

#### **1. Completar UI del Dashboard** (1-2 horas)
```javascript
// Agregar en DashboardPage.js:
- Card "Pregunta del Día"
- Detectar si hay pregunta pendiente
- Modal de respuesta (texto/audio)
- Envío al endpoint /api/respuestas-lmv
```

#### **2. Configurar Cron Job**

**Opción A - Servidor Linux/Railway**:
```bash
# Editar crontab
crontab -e

# Agregar línea:
0 9 * * 1,3,5 cd /app/backend && python cron_notificaciones.py
```

**Opción B - Railway Cron Jobs**:
1. Ir a Railway Dashboard
2. Settings → Cron Jobs
3. Agregar: `0 9 * * 1,3,5`
4. Command: `python /app/backend/cron_notificaciones.py`

**Opción C - Servicio Externo (Cron-Job.org)**:
1. Crear cuenta en https://cron-job.org
2. Nuevo cron job:
   - URL: `https://tu-app.railway.app/api/cron/enviar-pregunta-dia`
   - Schedule: Lunes, Miércoles, Viernes a las 9:00 AM
   - Método: POST

#### **3. Probar Sistema Completo**

```bash
# Test manual del cron:
cd /app/backend
python cron_notificaciones.py

# Verificar logs:
tail -f /var/log/supervisor/backend.err.log

# Verificar en MongoDB:
db.respuestas_lmv.find().limit(5)
```

#### **4. Lanzamiento**

1. **Semana 0** (Pruebas):
   - Activar solo para 2-3 usuarios beta
   - Verificar que llegan notificaciones
   - Verificar que se capturan respuestas
   - Ajustar según feedback

2. **Semana 1** (Lanzamiento):
   - Activar para todos los usuarios
   - Comunicar a RRHH sobre el inicio
   - Monitorear métricas de participación

---

## 📊 **MONITOREO Y MANTENIMIENTO**

### **KPIs a Seguir:**
1. **Tasa de apertura**: % de usuarios que ven la notificación
2. **Tasa de respuesta**: % de usuarios que responden
3. **Tiempo promedio de respuesta**: Horas desde envío hasta respuesta
4. **Canal preferido**: Telegram vs Dashboard
5. **Rachas activas**: Usuarios con racha > 7 días

### **Logs a Revisar:**
```bash
# Logs del cron
tail -f /var/log/cron_lmv.log

# Logs del backend
tail -f /var/log/supervisor/backend.err.log | grep "L-M-V"

# Logs del bot de Telegram
tail -f /var/log/supervisor/backend.err.log | grep "Telegram"
```

### **Queries Útiles (MongoDB)**:
```javascript
// Tasa de respuesta semanal
db.respuestas_lmv.aggregate([
  { $match: { semana: 1 } },
  { $group: {
      _id: "$numero_envio",
      total: { $sum: 1 },
      respondidas: { $sum: { $cond: [{ $ne: ["$respuesta", null] }, 1, 0] } }
  }}
])

// Usuarios más activos
db.users.find().sort({ puntos_totales: -1 }).limit(10)

// Preguntas pendientes por usuario
db.respuestas_lmv.find({ user_id: "...", respuesta: null })
```

---

## 🔧 **TROUBLESHOOTING**

### **Problema: Notificaciones no llegan**
```bash
# 1. Verificar bot está activo
curl http://localhost:8001/api/telegram/status

# 2. Verificar cron se ejecutó
grep "CRON JOB" /var/log/cron_lmv.log

# 3. Verificar usuarios tienen telegram_chat_id
db.users.find({ telegram_chat_id: { $ne: null } }).count()
```

### **Problema: Respuestas no se capturan**
```bash
# 1. Verificar webhook del bot
# 2. Ver logs del telegram_webhook.py
# 3. Verificar que hay preguntas pendientes
db.respuestas_lmv.find({ respuesta: null }).count()
```

### **Problema: Puntos no se otorgan**
```bash
# Verificar endpoint de gamificación
grep "puntos_otorgados" /var/log/supervisor/backend.err.log
```

---

## 📞 **CONTACTO Y SOPORTE**

Para preguntas técnicas sobre este sistema:
- Revisar este documento primero
- Verificar logs del sistema
- Contactar al equipo de desarrollo

---

**Última actualización**: 11 Noviembre 2025  
**Versión**: 1.0 MVP  
**Estado**: Preparado para activación
