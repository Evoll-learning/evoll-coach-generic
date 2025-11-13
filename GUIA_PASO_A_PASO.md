# 🎯 GUÍA PASO A PASO - DE EMERGENT A PRODUCCIÓN

Julio, sigue estos pasos **EN ORDEN** para tener EvoLL funcionando en Railway con tu propia URL.

---

## 📱 PASO 1: SUBIR A GITHUB (Desde Emergent)

### 1.1 Ir al chat de Emergent
En Emergent, donde estás ahora, hay una opción arriba que dice **"Save to Github"** o similar.

### 1.2 Conectar GitHub
1. Click en "Save to Github"
2. Autoriza Emergent a acceder a tu GitHub
3. Crea un nuevo repositorio:
   - Nombre: `evoll-orenes-mvp`
   - Privado: ✅ SÍ
   - Click "Create"

4. Emergent subirá automáticamente todo el código

✅ **Resultado**: Código en GitHub listo para Railway

---

## 🚂 PASO 2: CREAR CUENTA EN RAILWAY

### 2.1 Registrarse
1. Ve a [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Autoriza Railway

### 2.2 Verificar cuenta (importante)
1. Railway te pedirá verificar tu email
2. También necesitarás agregar una tarjeta (te dan $5 gratis)
3. Plan Hobby: $5/mes por servicio

✅ **Resultado**: Cuenta Railway activa

---

## 🔧 PASO 3: DEPLOYAR BACKEND

### 3.1 Crear proyecto
1. En Railway, click "**+ New Project**"
2. Selecciona "**Deploy from GitHub repo**"
3. Busca y selecciona `evoll-orenes-mvp`

### 3.2 Configurar Backend
Railway detectará automáticamente que hay código Python.

1. Click en el servicio que se creó
2. Ve a "**Settings**"
3. Configura:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Click "Deploy"

### 3.3 Agregar Variables de Entorno

1. Ve a la pestaña "**Variables**"
2. Click "**+ New Variable**"
3. Agrega TODAS estas (una por una):

```
JWT_SECRET_KEY=evoll-orenes-secret-key-production-2025
EMERGENT_LLM_KEY=sk-emergent-d3425B83116F351C27
TELEGRAM_BOT_TOKEN=8258706290:AAFGFapyppPeVmgpV0f-1EWxzG7x6EKcRf4
TELEGRAM_BOT_USERNAME=Evoll_Orenes_Bot
SUPABASE_URL=https://cqxflqimwisvnmhfvgyv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxeGZscWltd2lzdm5taGZ2Z3l2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3NzMzNjQsImV4cCI6MjA3ODM0OTM2NH0.R9iXBdmanVy34FPiqIsuS1vdthw7PphnfM0rAb2-YXA
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxeGZscWltd2lzdm5taGZ2Z3l2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2Mjc3MzM2NCwiZXhwIjoyMDc4MzQ5MzY0fQ.UU2fBjTOVPJTZUTIYIjTwf--Unsd6CGZJ-cgXtQGrYI
ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4
ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6nh516wm
CORS_ORIGINS=*
```

4. Click "**Add**" después de cada variable

### 3.4 Obtener URL del Backend

1. El backend se está deployando (tarda 2-3 minutos)
2. Cuando termine, ve a "**Settings**" → "**Networking**"
3. Verás un dominio tipo: `backend-production-XXXX.up.railway.app`
4. **COPIA ESTA URL** - la necesitas para el frontend

✅ **Resultado**: Backend funcionando en Railway

---

## 🎨 PASO 4: DEPLOYAR FRONTEND

### 4.1 Agregar nuevo servicio
1. En el mismo proyecto Railway, click "**+ New**"
2. Selecciona "**GitHub Repo**"
3. Elige de nuevo `evoll-orenes-mvp`

### 4.2 Configurar Frontend
1. Click en el nuevo servicio
2. Ve a "**Settings**"
3. Configura:
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn install && yarn build`
   - **Start Command**: `npx serve -s build -l $PORT`
4. **NO** hagas Deploy todavía

### 4.3 Agregar Variables de Entorno (Frontend)

1. Ve a "**Variables**"
2. Agrega estas 3 variables:

```
REACT_APP_BACKEND_URL=https://TU-BACKEND-URL-AQUI.up.railway.app
REACT_APP_ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4
REACT_APP_ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6nh516wm
```

⚠️ **IMPORTANTE**: 
- Reemplaza `TU-BACKEND-URL-AQUI` con la URL del backend del paso 3.4
- Ejemplo: `https://backend-production-a1b2.up.railway.app`

3. Ahora sí, click "**Deploy**"

### 4.4 Obtener URL del Frontend
1. Cuando termine de deployar (3-5 minutos)
2. Ve a "**Settings**" → "**Networking**"
3. Verás la URL del frontend: `frontend-production-XXXX.up.railway.app`
4. **¡Abre esa URL!** 🎉

✅ **Resultado**: Frontend funcionando

---

## 🧪 PASO 5: PROBAR QUE TODO FUNCIONA

### 5.1 Test básico
1. Abre la URL del frontend
2. Deberías ver la landing page de EvoLL
3. Click en "**Acceder**"

### 5.2 Test de Login
1. Email: `julio@evoll.es`
2. Password: `test123`
3. Deberías entrar al dashboard

### 5.3 Test completo
- ✅ Dashboard carga correctamente
- ✅ Sección L-M-V muestra las 6 preguntas
- ✅ Coach IA responde (prueba enviar mensaje)
- ✅ Comunidad permite publicar
- ✅ Gamificación muestra 50 puntos

Si TODO funciona, ¡ya tienes el MVP en producción! 🎊

---

## 🌐 PASO 6 (OPCIONAL): DOMINIO PERSONALIZADO

### 6.1 Comprar dominio (si no tienes)
- Recomendados: Namecheap, GoDaddy, Google Domains
- Ejemplo: `evoll-orenes.com`

### 6.2 Configurar en Railway - Frontend
1. Ve al servicio Frontend
2. Settings → Networking → "**+ Custom Domain**"
3. Agrega: `evoll-orenes.com` (o tu dominio)
4. Railway te dará instrucciones DNS
5. Ve a tu proveedor de dominio y agrega los registros DNS

### 6.3 Configurar en Railway - Backend
1. Ve al servicio Backend
2. Settings → Networking → "**+ Custom Domain**"
3. Agrega: `api.evoll-orenes.com` (subdominio)
4. Agrega registros DNS

### 6.4 Actualizar Frontend
1. Ve a Variables del Frontend
2. Cambia `REACT_APP_BACKEND_URL` a: `https://api.evoll-orenes.com`
3. Redeploy (Settings → Deploy → Redeploy)

⏱️ DNS tarda 5-30 minutos en propagarse

✅ **Resultado**: Tu propia URL profesional

---

## 👥 PASO 7: CREAR USUARIOS DE DEMO PARA RRHH

Ahora otros pueden registrarse:

1. Comparte la URL: `https://evoll-orenes.com` (o tu URL de Railway)
2. Los usuarios hacen:
   - Click "**Registrarse**"
   - Completan formulario
   - Completan onboarding
   - ¡Empiezan a usar la plataforma!

---

## 🎯 DEMO PARA RRHH - GUIÓN SUGERIDO

### Introducción (2 min)
"EvoLL es una plataforma de desarrollo de liderazgo con IA que combina coaching personalizado, reflexión estructurada y gamificación."

### Demo Coach IA (3 min)
1. Mostrar pregunta en dashboard
2. Hacer consulta al Coach IA
3. Mostrar respuesta con voz (ElevenLabs)

### Demo Sistema L-M-V (3 min)
1. Ir a sección "L-M-V"
2. Mostrar historial de respuestas
3. Responder pregunta pendiente

### Demo Comunidad (2 min)
1. Ir a Comunidad
2. Crear post de ejemplo
3. Mostrar interacción

### Demo Gamificación (2 min)
1. Mostrar puntos, nivel, racha
2. Mostrar leaderboard
3. Explicar badges

### Cierre (1 min)
"Usuarios reciben notificaciones por Telegram, pueden responder desde ahí, y todo se integra en una experiencia fluida de aprendizaje continuo."

---

## 📊 MONITOREO Y MANTENIMIENTO

### Ver logs en Railway
1. Click en el servicio (Backend o Frontend)
2. Ve a la pestaña "**Logs**"
3. Puedes ver errores en tiempo real

### Costos aproximados
- Backend: $5/mes
- Frontend: $5/mes
- **Total**: ~$10/mes

### Actualizaciones futuras
1. Haces cambios en Emergent
2. Guardas en GitHub (Save to Github)
3. Railway detecta cambios automáticamente
4. Redeploy automático en 2-3 minutos

---

## ❓ TROUBLESHOOTING RÁPIDO

### "No puedo hacer login"
- Verifica que el backend esté corriendo
- Revisa logs del backend
- Verifica variable `REACT_APP_BACKEND_URL`

### "Coach IA no responde"
- Verifica `EMERGENT_LLM_KEY` en backend
- Revisa logs para ver error específico

### "Frontend no carga"
- Verifica que el build se completó
- Revisa logs del frontend
- Verifica que `serve` esté instalado

### "Telegram no funciona"
- Normal, necesita configuración adicional
- Por ahora usa solo la web

---

## ✅ CHECKLIST FINAL ANTES DE DEMO

- [ ] Backend deployado y funcionando
- [ ] Frontend deployado y funcionando
- [ ] Puedes hacer login con julio@evoll.es
- [ ] Coach IA responde correctamente
- [ ] L-M-V muestra preguntas y respuestas
- [ ] Comunidad permite publicar
- [ ] Gamificación muestra puntos
- [ ] Otros pueden registrarse
- [ ] Dominio personalizado funcionando (opcional)
- [ ] Has probado desde otro navegador/dispositivo

---

## 🎉 ¡LISTO!

Ya tienes EvoLL funcionando en Railway, accesible desde cualquier lugar, con usuarios reales pudiendo registrarse y usar toda la plataforma.

**¿Preguntas? Contacta a tu desarrollador o revisa los logs en Railway.**

---

## 📞 SOPORTE

- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs
- GitHub Issues: (tu repo)

¡Mucha suerte con la demo a RRHH de Orenes! 🚀
