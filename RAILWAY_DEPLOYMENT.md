# 🚂 GUÍA DE DEPLOYMENT EN RAILWAY

## PASO 1: PREPARAR REPOSITORIO EN GITHUB

### 1.1 Crear repositorio en GitHub
1. Ve a [github.com](https://github.com)
2. Click en "New repository"
3. Nombre: `evoll-orenes-mvp`
4. Descripción: "Plataforma de Liderazgo con IA - Grupo Orenes"
5. **Privado** (importante)
6. **NO** marcar "Add README" (ya existe)
7. Click "Create repository"

### 1.2 Conectar y subir código
```bash
# En Emergent, ejecuta estos comandos:
cd /app
git init
git add .
git commit -m "MVP EvoLL - Listo para producción"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/evoll-orenes-mvp.git
git push -u origin main
```

---

## PASO 2: CREAR CUENTA EN RAILWAY

1. Ve a [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Login con GitHub
4. Autoriza Railway a acceder a tus repositorios

---

## PASO 3: DEPLOYAR BACKEND

### 3.1 Crear servicio Backend
1. Click "+ New"
2. Selecciona "Deploy from GitHub repo"
3. Busca `evoll-orenes-mvp`
4. Click en el repo

### 3.2 Configurar Backend
1. Railway detectará que es Python
2. **Root Directory**: `/backend`
3. **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Click "Deploy"

### 3.3 Agregar Variables de Entorno (Backend)

Ve a la pestaña "Variables" y agrega:

```env
JWT_SECRET_KEY=evoll-orenes-secret-key-change-in-production
EMERGENT_LLM_KEY=sk-emergent-d3425B83116F351C27
TELEGRAM_BOT_TOKEN=8258706290:AAFGFapyppPeVmgpV0f-1EWxzG7x6EKcRf4
TELEGRAM_BOT_USERNAME=Evoll_Orenes_Bot
SUPABASE_URL=https://cqxflqimwisvnmhfvgyv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxeGZscWltd2lzdm5taGZ2Z3l2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3NzMzNjQsImV4cCI6MjA3ODM0OTM2NH0.R9iXBdmanVy34FPiqIsuS1vdthw7PphnfM0rAb2-YXA
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxeGZscWltd2lzdm5taGZ2Z3l2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2Mjc3MzM2NCwiZXhwIjoyMDc4MzQ5MzY0fQ.UU2fBjTOVPJTZUTIYIjTwf--Unsd6CGZJ-cgXtQGrYI
ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4
ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6nh516wm
CORS_ORIGINS=*
PORT=8001
```

### 3.4 Obtener URL del Backend
1. Ve a "Settings" → "Networking"
2. Click "Generate Domain"
3. Copia la URL (ejemplo: `evoll-backend.up.railway.app`)
4. **Guarda esta URL** - la necesitarás para el frontend

---

## PASO 4: DEPLOYAR FRONTEND

### 4.1 Crear servicio Frontend
1. Click "+ New Service"
2. Selecciona el mismo repo `evoll-orenes-mvp`
3. Click "Deploy"

### 4.2 Configurar Frontend
1. **Root Directory**: `/frontend`
2. **Build Command**: `yarn install && yarn build`
3. **Start Command**: `npx serve -s build -l $PORT`

### 4.3 Agregar Variables de Entorno (Frontend)

```env
REACT_APP_BACKEND_URL=https://TU-BACKEND-URL.up.railway.app
REACT_APP_ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4
REACT_APP_ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6nh516wm
```

⚠️ **IMPORTANTE**: Reemplaza `TU-BACKEND-URL` con la URL real de tu backend del paso 3.4

### 4.4 Instalar `serve` en el frontend

Railway necesita `serve` para servir el build de React. Agrega a `/frontend/package.json`:

```json
{
  "dependencies": {
    ...
    "serve": "^14.2.0"
  }
}
```

---

## PASO 5: CONFIGURAR DOMINIO PERSONALIZADO (OPCIONAL)

### 5.1 Frontend - Dominio principal
1. Ve al servicio Frontend
2. Settings → Networking → Custom Domain
3. Agrega: `evoll.grupoorenes.com` (o el que tengas)
4. Sigue las instrucciones DNS de Railway

### 5.2 Backend - Subdominio API
1. Ve al servicio Backend
2. Settings → Networking → Custom Domain
3. Agrega: `api.evoll.grupoorenes.com`

### 5.3 Actualizar Frontend con nuevo dominio
1. Ve a Variables del Frontend
2. Cambia `REACT_APP_BACKEND_URL` a: `https://api.evoll.grupoorenes.com`
3. Redeploy

---

## PASO 6: VERIFICACIÓN POST-DEPLOYMENT

### 6.1 Verificar Backend
```bash
# Probar endpoint de health
curl https://TU-BACKEND-URL.up.railway.app/

# Probar login
curl -X POST https://TU-BACKEND-URL.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"julio@evoll.es","password":"test123"}'
```

### 6.2 Verificar Frontend
1. Abre la URL del frontend
2. Haz login con julio@evoll.es / test123
3. Verifica:
   - ✅ Coach IA responde
   - ✅ Preguntas L-M-V aparecen
   - ✅ Comunidad funciona
   - ✅ Gamificación muestra puntos

---

## PASO 7: CREAR USUARIOS DE PRUEBA

Una vez en producción, otros usuarios pueden:

1. Ir a tu URL: `https://evoll.grupoorenes.com`
2. Click en "Registrarse"
3. Completar onboarding
4. Empezar a usar la plataforma

---

## 🔧 TROUBLESHOOTING

### Error: "Cannot connect to backend"
- Verifica que `REACT_APP_BACKEND_URL` esté correcto
- Verifica que `CORS_ORIGINS=*` esté en el backend
- Mira los logs del backend en Railway

### Error: "500 Internal Server Error"
- Revisa logs del backend
- Verifica que todas las variables de entorno estén configuradas
- Verifica conexión a Supabase

### Telegram no funciona
- Configura webhook del bot para apuntar a tu backend
- O déjalo en modo polling (como está ahora)

---

## 📊 MONITOREO

Railway ofrece:
- **Logs en tiempo real**: Click en el servicio → Logs
- **Métricas**: CPU, RAM, Network
- **Alertas**: Configura en Settings

---

## 💰 COSTOS

Railway ofrece:
- **Plan Hobby**: $5/mes por servicio (2 servicios = $10/mes)
- **Plan Pro**: $20/mes con $10 de créditos incluidos

Para MVP: Plan Hobby es suficiente.

---

## ✅ CHECKLIST FINAL

- [ ] Código subido a GitHub
- [ ] Backend deployado en Railway
- [ ] Frontend deployado en Railway
- [ ] Variables de entorno configuradas
- [ ] Dominio personalizado conectado (opcional)
- [ ] Login funciona
- [ ] Coach IA responde
- [ ] L-M-V muestra preguntas
- [ ] Comunidad funciona
- [ ] Nuevos usuarios pueden registrarse

---

¡Listo para demostrar a RRHH de Orenes! 🎉
