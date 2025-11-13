# 🚂 GUÍA DE DEPLOYMENT EN RAILWAY

**Para**: Proyecto EvoLL Coach - Grupo Orenes  
**Fecha**: Noviembre 2025  
**Estado**: Listo para deployment

---

## 🎯 **¿POR QUÉ RAILWAY?**

Railway es la mejor opción para este proyecto porque:
- ✅ Deploy directo desde GitHub
- ✅ Dominio personalizado gratuito
- ✅ Variables de entorno fáciles
- ✅ MongoDB Atlas se puede integrar
- ✅ Cron jobs nativos
- ✅ Logs en tiempo real
- ✅ Escalado automático

---

## 📋 **PRE-REQUISITOS**

### **1. Cuenta de Railway**
- Crear cuenta en: https://railway.app
- Conectar con GitHub

### **2. Cuenta de MongoDB Atlas** (para reemplazar MongoDB local)
- Crear cuenta en: https://www.mongodb.com/cloud/atlas
- Crear cluster gratuito
- Obtener connection string

### **3. Repositorio GitHub**
- El código debe estar en un repositorio
- Branch principal: `main` o `master`

---

## 🔧 **PREPARACIÓN DEL PROYECTO**

### **1. Crear archivo `railway.json`**

Crear en la raíz del proyecto:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "supervisord -c /app/supervisord.conf",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **2. Crear `Procfile`** (opcional pero recomendado)

```
web: supervisord -c /app/supervisord.conf
```

### **3. Actualizar `requirements.txt`**

Asegurarse de que tiene todas las dependencias:
```txt
fastapi
uvicorn
motor
pymongo
python-dotenv
pydantic
pydantic-settings
pydantic[email]
bcrypt
passlib
python-jose[cryptography]
python-multipart
httpx
python-telegram-bot
emergentintegrations
supabase
```

### **4. Actualizar `.gitignore`**

```
.env
__pycache__/
*.pyc
.DS_Store
node_modules/
.venv/
venv/
*.log
```

---

## 🚀 **DEPLOYMENT PASO A PASO**

### **PASO 1: Configurar MongoDB Atlas**

#### **1.1. Crear Cluster**
1. Ve a https://cloud.mongodb.com
2. "Create" → "Shared" (gratis)
3. Selecciona región más cercana (ej: `eu-west-1`)
4. Nombre del cluster: `evoll-production`

#### **1.2. Configurar Database**
1. Database Access → Add New Database User
   - Username: `evoll_admin`
   - Password: (genera una segura y guárdala)
   - Role: `Atlas admin`

2. Network Access → Add IP Address
   - Click "Allow Access from Anywhere" (0.0.0.0/0)
   - Confirm

#### **1.3. Obtener Connection String**
1. Clusters → Connect
2. "Connect your application"
3. Driver: Python
4. Copiar connection string:
   ```
   mongodb+srv://evoll_admin:<password>@evoll-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Reemplazar `<password>` con tu contraseña
6. Agregar nombre de base de datos al final: `/evoll_db`

**Connection String Final**:
```
mongodb+srv://evoll_admin:TU_PASSWORD@evoll-production.xxxxx.mongodb.net/evoll_db?retryWrites=true&w=majority
```

---

### **PASO 2: Deployment en Railway**

#### **2.1. Crear Nuevo Proyecto**
1. Ve a https://railway.app/new
2. "Deploy from GitHub repo"
3. Selecciona tu repositorio
4. Branch: `main`

#### **2.2. Configurar Variables de Entorno**

En Railway Dashboard → Variables:

```env
# MongoDB
MONGO_URL=mongodb+srv://evoll_admin:PASSWORD@evoll-production.xxxxx.mongodb.net/evoll_db?retryWrites=true&w=majority
DB_NAME=evoll_db

# API Keys
EMERGENT_LLM_KEY=sk-emergent-d3425B83116F351C27
TELEGRAM_BOT_TOKEN=8258706290:AAFGFapyppPeVmgpV0f-1EWxzG7x6EKcRf4
TELEGRAM_BOT_USERNAME=Evoll_Orenes_Bot

# ElevenLabs
ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4
ELEVENLABS_AGENT_ID=agent_7001k9s8hn8ffc0sfepa6hn516wm

# Supabase (opcional por ahora)
SUPABASE_URL=https://cqxflqimwisvnmhfvgyv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Security
JWT_SECRET_KEY=production-secret-key-muy-segura-cambiar-esto
CORS_ORIGINS=*

# Frontend (Railway auto-genera esto)
REACT_APP_BACKEND_URL=https://tu-app.up.railway.app
```

#### **2.3. Deploy**
1. Railway detectará automáticamente el proyecto
2. Click "Deploy"
3. Esperar 5-10 minutos

#### **2.4. Obtener URL**
1. Settings → Domains
2. "Generate Domain"
3. Tu app estará en: `https://tu-app.up.railway.app`

---

### **PASO 3: Configurar Dominio Personalizado (Opcional)**

#### **3.1. Si tienes dominio propio** (ej: `coach.evoll.es`)

1. **En Railway**:
   - Settings → Domains
   - "Custom Domain"
   - Ingresar: `coach.evoll.es`
   - Railway te dará un CNAME record

2. **En tu proveedor de DNS** (ej: Cloudflare, GoDaddy):
   - Agregar CNAME record:
     - Name: `coach`
     - Target: `tu-app.up.railway.app`
     - TTL: Auto

3. **Esperar propagación** (5-30 minutos)

4. **Actualizar variable de entorno**:
   ```env
   REACT_APP_BACKEND_URL=https://coach.evoll.es
   ```

---

### **PASO 4: Migrar Datos de MongoDB Local a Atlas**

#### **4.1. Exportar desde MongoDB Local**

```bash
# Conectar a tu MongoDB local
mongodump --uri="mongodb://localhost:27017" --db=evoll_orenes --out=/tmp/evoll_backup

# Ver lo que se exportó
ls -lah /tmp/evoll_backup/evoll_orenes/
```

#### **4.2. Importar a MongoDB Atlas**

```bash
# Reemplazar con tu connection string de Atlas
mongorestore --uri="mongodb+srv://evoll_admin:PASSWORD@evoll-production.xxxxx.mongodb.net/evoll_db" /tmp/evoll_backup/evoll_orenes/

# Verificar
mongosh "mongodb+srv://evoll_admin:PASSWORD@evoll-production.xxxxx.mongodb.net/evoll_db"
> show collections
> db.users.countDocuments()
```

---

### **PASO 5: Configurar Cron Jobs**

Railway tiene soporte nativo para cron jobs.

#### **Opción A: Railway Cron Jobs** (Recomendado)

1. En Railway Dashboard
2. New Service → "Cron Job"
3. Configure:
   - **Schedule**: `0 9 * * 1,3,5` (Lunes, Miércoles, Viernes a las 9 AM)
   - **Command**: `python /app/backend/cron_notificaciones.py`
   - **Environment**: (mismas variables que el servicio principal)

#### **Opción B: Servicio Externo (Cron-Job.org)**

1. Crear cuenta en https://cron-job.org
2. New Cron Job:
   - Title: "EvoLL L-M-V Notifications"
   - URL: `https://tu-app.up.railway.app/api/cron/enviar-pregunta-dia`
   - Schedule: Custom
     - Minute: `0`
     - Hour: `9`
     - Day of Week: `Monday, Wednesday, Friday`
   - HTTP Method: POST
   - Enable notifications: Yes

---

## ✅ **VERIFICACIÓN POST-DEPLOYMENT**

### **Checklist de Verificación:**

```bash
# 1. Backend está corriendo
curl https://tu-app.up.railway.app/api/

# 2. Frontend carga
open https://tu-app.up.railway.app/

# 3. Login funciona
# Ir a la web y probar login

# 4. Telegram funciona
# Enviar /start a @Evoll_Orenes_Bot

# 5. MongoDB Atlas conectado
# Ver logs en Railway

# 6. ElevenLabs funciona
# Probar conversación de voz
```

### **Ver Logs en Railway:**

1. Dashboard → Tu proyecto
2. "View Logs"
3. Buscar errores (líneas en rojo)

---

## 🔍 **TROUBLESHOOTING COMÚN**

### **Error: Cannot connect to MongoDB**

**Síntoma**: `MongoServerError: Authentication failed`

**Solución**:
1. Verificar que password en connection string sea correcto
2. Verificar que IP 0.0.0.0/0 esté permitida en Network Access
3. Verificar que usuario tenga permisos de Atlas Admin

### **Error: Telegram bot conflict**

**Síntoma**: `Conflict: terminated by other getUpdates request`

**Solución**:
```bash
# Ejecutar script de limpieza
python /app/backend/stop_telegram_bot.py

# O desde Railway CLI
railway run python /app/backend/stop_telegram_bot.py
```

### **Error: Frontend no carga**

**Síntoma**: Página en blanco o 404

**Solución**:
1. Verificar que `REACT_APP_BACKEND_URL` esté configurado
2. Rebuildir frontend: `cd frontend && yarn build`
3. Verificar que supervisord.conf incluye frontend

### **Error: Variables de entorno no se leen**

**Síntoma**: `KeyError: 'MONGO_URL'`

**Solución**:
1. En Railway Dashboard → Variables
2. Verificar que TODAS las variables estén configuradas
3. Click "Redeploy" para aplicar cambios

---

## 📊 **MONITOREO EN PRODUCCIÓN**

### **1. Railway Dashboard**
- CPU usage
- Memory usage
- Network traffic
- Logs en tiempo real

### **2. MongoDB Atlas Monitoring**
- Connections
- Operations per second
- Storage used

### **3. Configurar Alertas**

En Railway:
1. Settings → Notifications
2. Configurar alertas para:
   - CPU > 80%
   - Memory > 80%
   - Deploy failed

---

## 💰 **COSTOS ESTIMADOS**

### **Railway**:
- Free tier: $5/mes de crédito
- Hobby plan: $5/mes
- **Estimado para este proyecto**: $10-15/mes

### **MongoDB Atlas**:
- Free tier (M0): 512 MB storage (suficiente para MVP)
- **Costo**: $0/mes

### **Total**: $10-15/mes (o gratis si usas free tiers)

---

## 🔐 **SEGURIDAD EN PRODUCCIÓN**

### **1. Cambiar Secrets**

❌ **NO uses** en producción:
- `JWT_SECRET_KEY=evoll-orenes-secret-key-change-in-production`

✅ **Genera nuevo**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### **2. CORS Configuración**

En producción, cambiar:
```env
# De:
CORS_ORIGINS=*

# A:
CORS_ORIGINS=https://coach.evoll.es,https://www.coach.evoll.es
```

### **3. HTTPS**
- Railway proporciona HTTPS automáticamente
- Verificar que todas las URLs usen `https://`

---

## 📞 **SOPORTE**

### **Railway Support**:
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Twitter: @Railway

### **MongoDB Atlas Support**:
- Docs: https://docs.atlas.mongodb.com
- Community: https://community.mongodb.com

---

## 🎉 **DEPLOYMENT CHECKLIST FINAL**

Antes de dar por terminado:

- [ ] MongoDB Atlas configurado y conectado
- [ ] Todas las variables de entorno en Railway
- [ ] Deployment exitoso (sin errores en logs)
- [ ] Frontend carga correctamente
- [ ] Login funciona
- [ ] Telegram bot responde
- [ ] ElevenLabs voz funciona
- [ ] Cron job configurado (si se activa)
- [ ] Dominio personalizado configurado (si aplica)
- [ ] Datos migrados de local a Atlas
- [ ] Secrets de producción actualizados
- [ ] CORS configurado correctamente
- [ ] Monitoreo y alertas configuradas

---

**¡Listo para producción!** 🚀

**Última actualización**: 11 Noviembre 2025  
**Versión**: 1.0
