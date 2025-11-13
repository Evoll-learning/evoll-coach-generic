# 📋 INSTRUCCIONES FINALES PARA MVP

---

## ✅ LO QUE ACABAMOS DE HACER:

1. **✅ Arreglado error de Telegram** - Validación de chat_id mejorada
2. **✅ UI Limpia** - Solo 2 cards: Voz funcionando + Llamadas "próximamente"
3. **⏳ Falta mejorar cierre de conversaciones** - Ver instrucciones abajo

---

## 🔧 PARA MEJORAR EL CIERRE DE CONVERSACIONES:

### **Ve a tu dashboard de ElevenLabs:**
https://elevenlabs.io/app/conversational-ai

### **Edita tu agente "EvoLL Coach de Liderazgo"**

### **En "Mensaje del sistema", AGREGA esto al final:**

```
IMPORTANTE SOBRE CIERRE DE CONVERSACIONES:

Después de 3-4 intercambios O cuando notes que el líder ya tiene claridad:
1. Resume el insight clave en 15 palabras máximo
2. Haz UNA pregunta de compromiso:
   - "¿Qué harás en las próximas 24 horas?"
   - "¿Qué pequeño paso darás hoy?"
   - "¿Cuándo tendrás esa conversación?"
3. Termina con: "Cuando quieras seguir hablando, aquí estaré. ¡Adelante!"

SEÑALES PARA CERRAR:
- El líder dice "gracias", "perfecto", "ya sé qué hacer"
- Ha recibido 2-3 consejos concretos
- Lleva más de 5 minutos en la conversación
- Pregunta lo mismo de diferentes formas (ya tiene la respuesta)

NO prolongues innecesariamente. Menos es más.
```

### **Guarda los cambios**

---

## 📸 DEPLOYMENT: GITHUB + RAILWAY

### **1. GitHub**

Ya tienes el código en el entorno de Emergent. Para guardarlo en GitHub:

**Opción A: Usar función "Save to GitHub" de Emergent**
- En la interfaz de Emergent, busca botón "Save to GitHub"
- Conecta tu repositorio
- Hace push automático

**Opción B: Manual (si tienes acceso SSH)**
```bash
cd /app
git init
git add .
git commit -m "MVP EvoLL Coach completo"
git remote add origin [tu-repo-github-url]
git push -u origin main
```

---

### **2. Railway Deployment**

**Requisitos previos:**
- Cuenta en Railway.app
- Repositorio en GitHub

**Pasos:**

1. **Ve a:** https://railway.app
2. **Login** con GitHub
3. **New Project** → "Deploy from GitHub repo"
4. **Selecciona** tu repositorio de EvoLL
5. **Railway detectará** automáticamente FastAPI + React
6. **Variables de entorno** - Agregar estas:

```bash
# Backend
MONGO_URL=mongodb://mongo:27017
DB_NAME=evoll_orenes
EMERGENT_LLM_KEY=sk-emergent-d3425B83116F351C27
TELEGRAM_BOT_TOKEN=8258706290:AAFGFapyppPeVmgpV0f-1EWxzG7x6EKcRf4
TELEGRAM_BOT_USERNAME=Evoll_Orenes_Bot

# Supabase
SUPABASE_URL=https://cqxflqimwisvnmhfvgyv.supabase.co
SUPABASE_ANON_KEY=[tu-key]
SUPABASE_SERVICE_ROLE_KEY=[tu-key]

# ElevenLabs
ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4
ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6nh516wm

# Frontend
REACT_APP_BACKEND_URL=https://[tu-app].railway.app
REACT_APP_ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6nh516wm
```

7. **Deploy** y esperar 5-10 minutos

8. **Personalizar URL:**
   - Settings → Domains
   - Puedes agregar dominio custom (ej: coach.evoll.es)
   - O usar el de Railway: `evoll-coach.up.railway.app`

---

## 🧪 TESTING FINAL ANTES DE ENVIAR MVP:

### **Checklist de funcionalidades:**

**Dashboard:**
- [ ] Login funciona
- [ ] Métricas se muestran (aunque sea en 40%)
- [ ] Pregunta del día aparece
- [ ] Audio en pregunta del día funciona
- [ ] Leaderboard visible (aunque esté vacío)

**Coach IA:**
- [ ] Chat de texto funciona
- [ ] Audio (grabar y enviar) funciona
- [ ] **VOZ (ElevenLabs)** funciona ✅
- [ ] Respuestas son naturales y empáticas

**Telegram:**
- [ ] Vinculación funciona
- [ ] Recibe mensaje de confirmación
- [ ] Puede responder preguntas directamente

**Gamificación:**
- [ ] Puntos se otorgan al responder
- [ ] Leaderboard se actualiza

---

## 📊 ESTADO FINAL DEL MVP:

| Funcionalidad | Estado | Prioridad |
|--------------|--------|-----------|
| **Voz conversacional** | ✅ | **CRÍTICA** |
| Chat texto | ✅ | ALTA |
| Audio transcripción | ✅ | ALTA |
| Telegram respuestas | ✅ | ALTA |
| Gamificación básica | ✅ | MEDIA |
| Métricas dinámicas | ✅ | MEDIA |
| Notificaciones L-M-V | ✅ | ALTA |
| Multi-tenant | ⏸️ | V2 |
| Analytics avanzados | ⏸️ | V2 |
| Supabase completo | ⏸️ | V2 |

---

## 🎯 PARA DEMO CON ORENES:

### **Puntos fuertes a destacar:**

1. **🎙️ Conversación de voz natural**
   - Como hablar con un mentor real
   - Sin necesidad de llamar por teléfono
   - Accesible desde cualquier navegador

2. **📱 Integración con Telegram**
   - Notificaciones diarias
   - Respuestas directas sin entrar a la web
   - Gamificación automática

3. **🎮 Gamificación**
   - Leaderboard competitivo
   - Badges y logros
   - Aumenta engagement

4. **📊 Seguimiento de progreso**
   - Métricas que evolucionan
   - 144 preguntas estructuradas
   - Metodología L-M-V implementada

5. **🤖 Coach IA empático**
   - Prompt socrático profesional
   - Preguntas poderosas
   - Valores de Orenes integrados

---

## 💰 COSTOS MENSUALES ESTIMADOS:

**Para 20 usuarios activos:**

- **ElevenLabs:** $5-22/mes (Starter o Creator)
- **Emergent LLM:** ~$10-20/mes (GPT-4o + Whisper)
- **Railway:** $5-10/mes (hosting)
- **Supabase:** Gratis (hasta 500MB)
- **MongoDB:** Gratis (si usas Atlas free tier)

**TOTAL:** $20-52/mes para MVP con 20 usuarios

---

## 📞 SOPORTE:

Si algo falla o necesitas ayuda:

1. **Logs del backend:**
   ```bash
   tail -f /var/log/supervisor/backend.err.log
   ```

2. **Logs del frontend:**
   ```bash
   tail -f /var/log/supervisor/frontend.err.log
   ```

3. **Reiniciar servicios:**
   ```bash
   sudo supervisorctl restart all
   ```

---

## ✅ PRÓXIMOS PASOS (Post-MVP):

1. **Validar con Orenes** (1-2 semanas)
2. **Recoger feedback** de primeros usuarios
3. **Iterar** según feedback
4. **Escalar:** Multi-tenant, analytics, integraciones
5. **Migración completa** a Supabase

---

**🎉 ¡MVP COMPLETO Y LISTO PARA DEMO!** 🚀

---

FIN DEL DOCUMENTO
