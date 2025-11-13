# 🤖 GUÍA RÁPIDA: Crear Bot de Telegram para EvoLL

## ✅ PASO 1: Crear el Bot (5 minutos)

### 1. Abre Telegram en tu móvil o desktop
- Busca: **@BotFather**
- Es el bot oficial de Telegram (tiene verificación azul)

### 2. Inicia conversación
- Envía: `/start`
- Envía: `/newbot`

### 3. Configura tu bot
BotFather te preguntará:

**Pregunta 1: Name of your bot?**
```
EvoLL Orenes
```
(Este es el nombre visible, puede tener espacios)

**Pregunta 2: Username for your bot?**
```
EvoLLOrenesBot
```
(Debe terminar en "bot" o "Bot", sin espacios)

### 4. ¡IMPORTANTE! Guarda el TOKEN
BotFather te dará algo como:
```
6234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
```

**⚠️ NO COMPARTAS ESTE TOKEN CON NADIE**

---

## ✅ PASO 2: Configurar en el Backend (2 minutos)

### Agrega el token al archivo .env

```bash
# Editar /app/backend/.env
TELEGRAM_BOT_TOKEN="TU_TOKEN_AQUI"
```

Ejemplo:
```bash
TELEGRAM_BOT_TOKEN="6234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"
```

---

## ✅ PASO 3: Reiniciar Backend

```bash
sudo supervisorctl restart backend
```

---

## ✅ PASO 4: Obtener tu Chat ID (para testing)

### Opción A: Usando un bot auxiliar
1. Busca en Telegram: **@userinfobot**
2. Envía `/start`
3. Te dará tu **Chat ID** (número como 123456789)

### Opción B: Hablando con tu bot
1. Busca tu bot: **@EvoLLOrenesBot** (o el nombre que pusiste)
2. Envía `/start`
3. Ve al navegador y abre:
```
https://api.telegram.org/bot{TU_TOKEN}/getUpdates
```
4. Busca `"chat":{"id":123456789}`

---

## ✅ PASO 5: Probar el Bot

### Desde la API:

```bash
# Test endpoint
curl -X GET "https://coach-ai-9.preview.emergentagent.com/api/telegram/status"

# Debería responder:
# {"activo": true, "bot_configurado": true}
```

### Enviar notificación de prueba:

```bash
# Primero, configura tu chat_id en la base de datos
curl -X POST "https://coach-ai-9.preview.emergentagent.com/api/telegram/configurar" \
  -H "Authorization: Bearer TU_TOKEN_USUARIO" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_chat_id": "TU_CHAT_ID",
    "notificaciones_activas": true
  }'

# Luego, envía test
curl -X POST "https://coach-ai-9.preview.emergentagent.com/api/telegram/test" \
  -H "Authorization: Bearer TU_TOKEN_USUARIO"
```

**Deberías recibir un mensaje en Telegram con:**
```
🎯 ¡Nueva pregunta EvoLL!
...
```

---

## 🎯 PERSONALIZACIÓN DEL BOT

### Cambiar foto de perfil
1. En chat con @BotFather
2. Envía: `/setuserpic`
3. Selecciona tu bot
4. Envía la imagen (logo Orenes verde)

### Cambiar descripción
1. `/setdescription`
2. Selecciona tu bot
3. Escribe:
```
Bot oficial de EvoLL - Programa de Liderazgo Evolutivo del Grupo Orenes.
Recibe notificaciones de tus preguntas L-M-V semanales.
```

### Agregar comandos
1. `/setcommands`
2. Selecciona tu bot
3. Pega:
```
start - Iniciar el bot
help - Obtener ayuda
config - Configurar notificaciones
```

---

## 📱 CÓMO LO USARÁN LOS MANAGERS

### Configuración inicial (una vez)

1. **Manager busca el bot en Telegram:**
   - Busca: `@EvoLLOrenesBot`
   - Clic en "Start"

2. **Bot responde con instrucciones:**
   ```
   ¡Bienvenido a EvoLL! 
   
   Para activar notificaciones:
   1. Copia este código: [CODIGO]
   2. Ve a tu perfil en evoll.com
   3. Pega el código en "Notificaciones Telegram"
   ```

3. **Manager va a la plataforma:**
   - Perfil → Notificaciones
   - Pega su Chat ID
   - Activa notificaciones

4. **¡Listo!** Ahora recibirá:
   - Notificaciones cada L-M-V con la pregunta del día
   - Recordatorios si no ha respondido
   - Link directo para responder

---

## 🔔 PROGRAMAR NOTIFICACIONES AUTOMÁTICAS

### Usando cron (Linux)

```bash
# Editar crontab
crontab -e

# Agregar líneas para L-M-V a las 9:00 AM
0 9 * * 1,3,5 curl -X POST https://coach-ai-9.preview.emergentagent.com/api/telegram/notificar-todos
```

### Usando n8n (Recomendado)

1. Workflow trigger: Schedule (L-M-V 9:00 AM)
2. HTTP Request → `GET /api/users` (obtener todos activos)
3. Loop usuarios
4. Para cada uno:
   - GET pregunta del día
   - POST notificación Telegram

---

## 🛠️ TROUBLESHOOTING

### El bot no responde
```bash
# Verificar status
curl https://coach-ai-9.preview.emergentagent.com/api/telegram/status

# Verificar logs del backend
tail -f /var/log/supervisor/backend.err.log
```

### Error "Chat not found"
- El usuario debe escribir `/start` al bot primero
- Verificar que el chat_id sea correcto

### Token inválido
- Verificar que el token esté bien copiado en .env
- No debe tener espacios ni comillas extras

---

## 💡 PRÓXIMOS PASOS

1. ✅ **Crear bot con BotFather** (hecho si seguiste esta guía)
2. ✅ **Configurar token en backend** 
3. ⏳ **Crear workflow n8n para notificaciones automáticas**
4. ⏳ **Agregar botón "Configurar Telegram" en perfil de usuario**
5. ⏳ **Diseñar mensajes con formato bonito (Markdown)**

---

## 📊 EJEMPLO DE MENSAJE FINAL

Cuando todo funcione, managers recibirán:

```
🎯 ¡Nueva pregunta EvoLL!

📅 Semana 15 • P2
🏷️ Tipo: Reflexiva
💡 Competencia: Inteligencia Emocional

Pregunta:
¿Qué emociones te dan información valiosa sobre 
situaciones? ¿Cómo distingues intuición de reactividad?

👉 Responder ahora: https://evoll.com/dashboard

Tiempo estimado: 2-3 minutos
```

---

## ✅ CHECKLIST FINAL

- [ ] Bot creado con @BotFather
- [ ] Token guardado en /app/backend/.env
- [ ] Backend reiniciado
- [ ] Endpoint /telegram/status responde activo:true
- [ ] Probado con tu chat_id personal
- [ ] Recibido notificación de prueba en Telegram
- [ ] Personalizado nombre, foto, descripción del bot

**¡Listo para producción!** 🚀
