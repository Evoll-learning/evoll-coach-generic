# 📚 EVOLL LIDERAZGO ORENES - ESTADO DEL PROYECTO
**Fecha última actualización:** 10 Noviembre 2025
**Versión:** MVP en desarrollo

---

## 🎯 OBJETIVO DEL PROYECTO

Plataforma de liderazgo evolutivo para Grupo Orenes con:
- Programa de 12 meses (5 módulos)
- Sistema L-M-V (Liderazgo, Management, Valores)
- 3 preguntas semanales (Lunes/Miércoles/Viernes)
- Coach IA (texto, audio, voz)
- Notificaciones por Telegram
- Gamificación (puntos, badges, leaderboard)
- Dashboards para usuarios, HR, e Inspector FUNDAE

---

## ✅ LO QUE ESTÁ FUNCIONANDO (100%)

### **Backend:**
- ✅ FastAPI corriendo en puerto 8001
- ✅ MongoDB local funcionando (temporal, migraremos a Supabase)
- ✅ Telegram Bot activo: `@Evoll_Orenes_Bot`
  - Token: `8258706290:AAFGFapyppPeVmgpV0f-1EWxzG7x6EKcRf4`
  - Webhook handler implementado
  - Comandos: /start, /ayuda, /estado, /activar, /desactivar
- ✅ Coach IA con emergentintegrations
  - GPT-4o para texto
  - Whisper para audio (transcripción)
  - Respuestas en formato markdown
- ✅ 144 preguntas L-M-V cargadas en `preguntas_lmv_completas.py`
- ✅ Endpoints de autenticación (registro/login)
- ✅ Sistema de vinculación de Telegram

### **Frontend:**
- ✅ React + Tailwind CSS
- ✅ Páginas: Landing, Onboarding, Dashboard, Comunidad, Coach IA, Perfil
- ✅ Tema oscuro con colores de Orenes (#10b981 verde)
- ✅ Tipografía: Poppins
- ✅ Input/Textarea con contraste corregido (texto negro visible)
- ✅ Coach IA con:
  - Envío de mensajes de texto
  - Grabación y envío de audio
  - Respuestas en markdown
  - UX mejorada (banner de grabación claro)
- ✅ Perfil con sección de vinculación de Telegram
  - Instrucciones claras
  - Botón de prueba
  - Opción de desvincular

### **Supabase:**
- ✅ Proyecto creado: `evoll-liderazgo-orenes`
- ✅ URL: `https://cqxflqimwisvnmhfvgyv.supabase.co`
- ✅ 8 tablas creadas:
  - users
  - respuestas_lmv
  - conversaciones_coach
  - telegram_messages
  - badges (6 badges iniciales insertados)
  - user_badges
  - actividades
  - user_sessions
- ✅ RLS Policies configuradas
- ✅ Views: leaderboard, user_progress
- ✅ 4 usuarios migrados de MongoDB

---

## ⏳ LO QUE FALTA POR IMPLEMENTAR

### **PRIORIDAD ALTA (Para este MVP):**

#### **1. Notificaciones Automáticas L-M-V**
- [ ] Crear endpoint `/api/cron/enviar-pregunta-dia`
- [ ] Lógica de selección de pregunta según día (Lunes=Liderazgo, Miércoles=Management, Viernes=Valores)
- [ ] Envío masivo a todos los usuarios con `telegram_chat_id`
- [ ] Guardar pregunta enviada en tabla `respuestas_lmv`
- [ ] Configurar cron job (diario 9AM)

**Archivos a modificar:**
- `/app/backend/server.py` (nuevo endpoint)
- `/app/backend/preguntas_lmv_completas.py` (ya existe)

---

#### **2. VAPI - Llamadas de Voz** 🎙️
- [ ] Configurar Assistant en dashboard.vapi.ai
  - Prompt del coach en español
  - Voz en español (es-ES)
  - Knowledge base con metodología L-M-V
- [ ] Obtener Assistant ID
- [ ] Crear endpoint `/api/coach/iniciar-llamada-vapi`
- [ ] Botón "📞 Llamar a mi Coach" en CoachIAPage
- [ ] Integración con emergentintegrations si es posible

**API Key disponible:** `0067fab5-0e9f-4085-8277-a163f79a3215`

**Archivos a crear/modificar:**
- `/app/backend/vapi_integration.py` (nuevo)
- `/app/backend/server.py` (nuevo endpoint)
- `/app/frontend/src/pages/CoachIAPage.js` (botón de llamada)

---

#### **3. Gamificación**
- [ ] Sistema de puntos automático:
  - Responder pregunta L-M-V: +10 puntos
  - Consultar coach: +5 puntos
  - Racha 7 días: +50 puntos
- [ ] Otorgamiento automático de badges:
  - Verificar criterios en cada acción
  - Insertar en `user_badges`
  - Notificar al usuario
- [ ] Leaderboard visible en Dashboard
  - Usar view `leaderboard` de Supabase
  - Top 10 usuarios

**Archivos a modificar:**
- `/app/backend/server.py` (lógica de puntos)
- `/app/frontend/src/pages/DashboardPage.js` (mostrar leaderboard)

---

#### **4. Recepción de Respuestas vía Telegram**
- [ ] Handler en telegram_webhook.py para asociar mensajes con preguntas
- [ ] Guardar respuesta en `respuestas_lmv`
- [ ] Otorgar puntos automáticamente
- [ ] Feedback al usuario por Telegram

**Archivos a modificar:**
- `/app/backend/telegram_webhook.py`

---

### **PRIORIDAD MEDIA (Puede esperar):**

#### **5. Migración Completa a Supabase**
- [ ] Actualizar server.py para usar Supabase Auth
- [ ] Migrar todos los endpoints de MongoDB a Supabase
- [ ] Actualizar frontend para usar Supabase Auth
- [ ] Eliminar dependencia de MongoDB

**Nota:** Decidimos posponer esto para mantener estabilidad. MongoDB funciona bien como solución temporal.

---

#### **6. Multi-Tenant (Roles y Dashboards)**
- [ ] Implementar roles: alumno, hr_admin, super_admin, inspector
- [ ] Dashboard para HR (ver todos los empleados de su empresa)
- [ ] Dashboard para Inspector FUNDAE (métricas anónimas agregadas)
- [ ] RLS policies por empresa_id

**Tablas ya preparadas en Supabase**

---

#### **7. Time Tracking**
- [ ] Frontend: trackear tiempo en cada página
- [ ] Guardar sesiones en `user_sessions`
- [ ] Reportes para FUNDAE

---

#### **8. Evaluación Mensual Automática**
- [ ] Cron job mensual
- [ ] GPT-4o genera informe personalizado
- [ ] Envío vía Telegram/Email

---

### **PRIORIDAD BAJA (V2):**

- [ ] WhatsApp notifications vía Twilio
- [ ] n8n workflows
- [ ] Integración con Readme LMS
- [ ] Panel de contenidos por módulo
- [ ] Analytics avanzados

---

## 📂 ESTRUCTURA DE ARCHIVOS IMPORTANTE

```
/app/
├── backend/
│   ├── server.py ⭐ (Main backend - MongoDB activo)
│   ├── server_mongodb_backup.py (Backup)
│   ├── .env ⭐ (Credenciales)
│   ├── requirements.txt
│   ├── telegram_bot.py (Notificaciones)
│   ├── telegram_webhook.py ⭐ (Recepción de mensajes)
│   ├── coach_ia_integration.py ⭐ (GPT-4o + Whisper)
│   ├── preguntas_lmv_completas.py ⭐ (144 preguntas)
│   ├── supabase_client.py (Cliente Supabase)
│   ├── supabase_schema.sql (Schema completo)
│   ├── migrate_mongodb_to_supabase.py (Ya ejecutado)
│   └── verificar_supabase.py (Testing)
│
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── OnboardingPage.js
│   │   │   ├── DashboardPage.js ⭐ (Agregar leaderboard aquí)
│   │   │   ├── ComunidadPage.js
│   │   │   ├── CoachIAPage.js ⭐ (Agregar botón VAPI aquí)
│   │   │   └── PerfilPage.js ⭐ (Telegram vinculación)
│   │   ├── components/ui/
│   │   │   ├── input.jsx ⭐ (Corregido)
│   │   │   └── textarea.jsx ⭐ (Corregido)
│   │   └── context/
│   │       └── AuthContext.js
│   ├── package.json
│   └── .env ⭐
│
└── test_result.md ⭐ (Testing protocol)
```

---

## 🔑 CREDENCIALES Y CONFIGURACIÓN

### **Backend (.env):**
```bash
MONGO_URL="mongodb://localhost:27017"
DB_NAME="evoll_orenes"
EMERGENT_LLM_KEY="sk-emergent-d3425B83116F351C27"
TELEGRAM_BOT_TOKEN="8258706290:AAFGFapyppPeVmgpV0f-1EWxzG7x6EKcRf4"
TELEGRAM_BOT_USERNAME="Evoll_Orenes_Bot"

# Supabase
SUPABASE_URL="https://cqxflqimwisvnmhfvgyv.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxeGZscWltd2lzdm5taGZ2Z3l2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3NzMzNjQsImV4cCI6MjA3ODM0OTM2NH0.R9iXBdmanVy34FPiqIsuS1vdthw7PphnfM0rAb2-YXA"
SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNxeGZscWltd2lzdm5taGZ2Z3l2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2Mjc3MzM2NCwiZXhwIjoyMDc4MzQ5MzY0fQ.UU2fBjTOVPJTZUTIYIjTwf--Unsd6CGZJ-cgXtQGrYI"

# VAPI (pendiente configurar Assistant)
VAPI_API_KEY="0067fab5-0e9f-4085-8277-a163f79a3215"
```

### **Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=https://[deployment-url]/api
```

### **URLs:**
- **Preview**: https://coach-ai-9.preview.emergentagent.com
- **Supabase Dashboard**: https://supabase.com/dashboard/project/cqxflqimwisvnmhfvgyv
- **Telegram Bot**: @Evoll_Orenes_Bot

---

## 🧪 COMANDOS ÚTILES

### **Backend:**
```bash
# Reiniciar servicios
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all

# Ver logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log

# Verificar Supabase
cd /app/backend && python verificar_supabase.py

# Testing
cd /app/backend && python migrate_mongodb_to_supabase.py
```

### **Instalación de dependencias:**
```bash
# Backend
cd /app/backend
pip install [package]
pip freeze > requirements.txt

# Frontend
cd /app/frontend
yarn add [package]
```

---

## 📝 DECISIONES TÉCNICAS IMPORTANTES

### **1. Por qué MongoDB + Supabase coexisten:**
- MongoDB está funcionando perfectamente para el MVP
- Supabase está configurado y listo para migración futura
- Evitamos riesgo de romper funcionalidad existente
- Migración completa se hará en fase posterior

### **2. Por qué Telegram en lugar de WhatsApp:**
- Más privado (no pertenece a Meta)
- Gratis (WhatsApp vía Twilio cuesta ~€0.01-0.02/mensaje)
- API más simple y robusta
- Cumple GDPR europeo
- Setup más rápido

### **3. Emergent LLM Key:**
- Permite usar GPT-4o y Whisper sin API keys propias
- Budget compartido, auto-recarga disponible
- Funciona con emergentintegrations

### **4. VAPI para voz:**
- Especializado en conversaciones de voz
- Mejor que implementar desde cero con Twilio
- Usuario ya tiene API key

---

## 🚨 PROBLEMAS CONOCIDOS Y SOLUCIONES

### **Problema 1: Backend no inicia**
**Síntoma:** Error en logs de supervisor
**Solución:**
```bash
tail -n 50 /var/log/supervisor/backend.err.log
# Revisar imports faltantes
pip install [missing-package]
sudo supervisorctl restart backend
```

### **Problema 2: Telegram bot no responde**
**Síntoma:** Usuario envía /start pero no recibe respuesta
**Solución:**
1. Verificar que backend esté corriendo
2. Verificar logs: `tail -f /var/log/supervisor/backend.err.log`
3. Verificar token en .env

### **Problema 3: Frontend no se conecta a backend**
**Síntoma:** Errores CORS o 404
**Solución:**
1. Verificar REACT_APP_BACKEND_URL en frontend/.env
2. Verificar que todos los endpoints backend tengan prefijo `/api`
3. Reiniciar servicios

---

## 📊 ESTADO DE TABLAS SUPABASE

| Tabla | Registros | Estado | Uso |
|-------|-----------|--------|-----|
| users | 4 | ✅ OK | Usuarios migrados |
| badges | 6 | ✅ OK | Badges iniciales |
| respuestas_lmv | 0 | ⏳ Pendiente | Se llenará con notificaciones |
| conversaciones_coach | 0 | ⏳ Pendiente | Se llenará con uso |
| telegram_messages | 0 | ⏳ Pendiente | Se llenará con uso |
| user_badges | 0 | ⏳ Pendiente | Gamificación |
| actividades | 0 | ⏳ Pendiente | Tracking |
| user_sessions | 0 | ⏳ Pendiente | Time tracking |

---

## 🎯 SIGUIENTE SESIÓN - CHECKLIST

Si necesitas continuar en otra sesión, empieza aquí:

### **1. Verificar estado:**
```bash
sudo supervisorctl status
cd /app/backend && python verificar_supabase.py
```

### **2. Revisar este documento:**
- Leer sección "LO QUE FALTA POR IMPLEMENTAR"
- Priorizar según necesidades

### **3. Continuar con:**
- Notificaciones automáticas L-M-V (PRIORIDAD)
- VAPI integration (DIFERENCIADOR)
- Gamificación (ENGAGEMENT)

---

## 📞 CONTACTO Y RECURSOS

**Usuario:** Julio (julio@evoll.es)
**Proyecto:** EvoLL Liderazgo - Grupo Orenes
**Empresa:** evoll.es

**Recursos:**
- Excel original con 144 preguntas (ya parseado en código)
- Documentación técnica completa en Supabase
- Backup de código en server_mongodb_backup.py

---

**Última actualización:** 10 Nov 2025 - Sesión de migración a Supabase completada
**Próximo hito:** Implementar notificaciones L-M-V + VAPI

---

## ⚡ REGLAS DE ORO PARA PRÓXIMAS SESIONES

1. **NUNCA borrar o modificar** las tablas de Supabase sin backup
2. **SIEMPRE hacer backup** antes de cambios grandes en server.py
3. **PROBAR en pequeños pasos** - cada cambio debe ser verificable
4. **LEER este documento COMPLETO** antes de cualquier cambio
5. **ACTUALIZAR este documento** después de implementar nuevas features

---

FIN DEL DOCUMENTO
