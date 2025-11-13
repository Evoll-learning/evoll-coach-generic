# 📱 SETUP TWILIO + VAPI PARA EVOLL

## 🎯 ARQUITECTURA PROPUESTA

```
Usuario WhatsApp ← Twilio WhatsApp API ← FastAPI Backend ← MongoDB
                                              ↓
                                         VAPI (Llamadas Voz)
```

---

## 📞 VAPI - VOICE AI

### API Key Obtenida
✅ **Ya tienes API key de VAPI lista para usar**

### Uso Recomendado
- **Para:** Llamadas de voz con el Coach IA
- **Casos de uso:**
  - Practicar conversaciones de feedback (rol-play)
  - Consultas rápidas por voz mientras estás en movimiento
  - Entrenamiento de comunicación verbal

### Costo
- Aproximadamente $0.10-0.15/minuto
- Para 350 managers con ~5 min/semana = ~$2,625/mes máximo
- **Recomendación:** Ofrecer 10 min gratuitos/mes por manager, luego opcional

### Integración (Próxima Fase)
```python
# Backend - Endpoint para iniciar llamada VAPI
@api_router.post("/vapi/iniciar-llamada")
async def iniciar_llamada_vapi(user: User = Depends(get_current_user)):
    # VAPI SDK integration
    call = vapi.create_call(
        assistant_id="assistant_id",
        phone_number=user.telefono,
        context=f"Usuario: {user.nombre}, Rol: {user.cargo}"
    )
    return {"call_id": call.id}
```

---

## 💬 TWILIO - WHATSAPP MESSAGING

### ¿Qué necesitas para crear cuenta Twilio?

**Documentos requeridos (España):**
1. **Identificación Personal:**
   - DNI o Pasaporte (PDF, JPEG o PNG)
   - Número del documento
   - Fecha de emisión y vencimiento
   
2. **Verificación de Dirección:**
   - Dirección física en España (no apartados postales)
   - Puede ser factura de servicios, extracto bancario
   
3. **Número de teléfono para verificación:**
   - Tu número personal para recibir código SMS
   
4. **Para mensajería a España (Importante):**
   - **Letter of Authorization (LOA)** - Carta de autorización
   - Requerido para usar Sender IDs alfanuméricos en España
   - Twilio proporciona template

**Proceso:**
1. Registro en twilio.com/try-twilio
2. Verificar email y teléfono
3. Subir documentos en Console → Phone Number Identity
4. Esperar aprobación (1-3 días hábiles)
5. Comprar número o configurar WhatsApp Business API

### Costo Twilio WhatsApp
- **Mensajes entrantes:** Gratis
- **Mensajes salientes:** $0.005 por mensaje
- **Para 350 managers × 3 mensajes/semana × 4 semanas = 4,200 mensajes/mes**
- **Costo mensual:** ~$21/mes (muy económico)

### Alternativas MÁS FÁCILES (Sin documentos complejos)

#### Opción A: WATI.io (Recomendado para empezar)
- **No requiere documentos LOA**
- **Precio:** $49/mes (incluye WhatsApp Business API)
- **Límite:** 1,000 conversaciones/mes
- **Setup:** 15 minutos
- **Ideal para:** Piloto y primeros 100 managers
- **Ventaja:** Interfaz visual, no-code

#### Opción B: Telegram Bot (MUY FÁCIL, GRATIS)
- **Sin documentos**
- **Sin costos**
- **Setup:** 5 minutos con BotFather
- **Desventaja:** Menos adopción que WhatsApp en España
- **Ventaja:** API muy simple, gratis totalmente

---

## 🚀 PLAN DE IMPLEMENTACIÓN RECOMENDADO

### FASE 1 - INMEDIATA (Sin esperar aprobaciones)

**Opción Telegram Bot (5 minutos):**
```python
# 1. Crear bot con @BotFather en Telegram
# 2. Obtener token
# 3. Instalar en backend
pip install python-telegram-bot

# 4. Código simple
from telegram import Bot

bot = Bot(token="TU_TOKEN")

# Enviar notificación
await bot.send_message(
    chat_id=user_telegram_id,
    text="🎯 ¡Nueva pregunta EvoLL!\n\n{pregunta}\n\nResponde en: https://evoll.com/dashboard"
)
```

**Ventajas:**
- ✅ Implementación inmediata
- ✅ Sin costos
- ✅ Sin burocracia
- ✅ API muy confiable
- ✅ Soporte de audio nativo (para respuestas por voz)

**Desventajas:**
- ❌ Requiere que managers instalen Telegram
- ❌ Menos familiar que WhatsApp en España

### FASE 2 - PROFESIONAL (1-2 semanas)

**Opción WATI.io:**

1. **Registro:** https://app.wati.io/register
2. **Setup (15 min):**
   - Conectar tu número WhatsApp Business
   - Verificar con código
   - Configurar templates de mensajes
3. **Integración API:**
```python
import requests

def enviar_whatsapp_wati(telefono, mensaje):
    url = "https://live-server-XXXX.wati.io/api/v1/sendTemplateMessage"
    headers = {
        "Authorization": "Bearer TU_API_KEY",
        "Content-Type": "application/json"
    }
    data = {
        "whatsappNumber": telefono,
        "template_name": "evoll_pregunta_dia",
        "parameters": [{"name": "pregunta", "value": mensaje}]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()
```

### FASE 3 - ENTERPRISE (Si escalan a 500+)

**Twilio WhatsApp Business API:**
- Requiere documentos LOA
- Proceso de aprobación 3-5 días
- Sin límites de volumen
- Más control y features

---

## 🔗 INTEGRACIÓN CON N8N (AUTOMATIZACIÓN)

### Setup n8n + Telegram (Más fácil)

```yaml
# Workflow n8n
1. Trigger: Cron (L-M-V 9:00 AM)
2. MongoDB: Query usuarios activos
3. ForEach Usuario:
   - Get pregunta del día (API EvoLL)
   - Send Telegram message
   - Log envío en MongoDB
```

### Setup n8n + WATI

```yaml
# Similar pero con WATI API node
1. Trigger: Cron (L-M-V 9:00 AM)
2. MongoDB: Query usuarios activos  
3. ForEach Usuario:
   - Get pregunta del día (API EvoLL)
   - WATI: Send WhatsApp Template
   - Log envío
```

---

## 💡 MI RECOMENDACIÓN PARA ORENES

### Para DEMO/PRESENTACIÓN (Esta semana):
✅ **Usar Telegram Bot**
- Setup en 10 minutos
- Funciona perfectamente
- Gratis
- Puedes demostrar notificaciones reales

### Para PRODUCCIÓN (Si aprueban):

**Mes 1-2 (100-200 managers):**
✅ **WATI.io** - $49/mes
- Fácil setup
- WhatsApp Business oficial
- Sin burocracia LOA

**Mes 3+ (300-500+ managers):**
✅ **Twilio** - $20-50/mes
- Necesitas LOA
- Más económico a escala
- Control total

---

## 📋 SIGUIENTE PASO INMEDIATO

**¿Qué prefieres para la DEMO con Orenes?**

### Opción 1: Telegram (RÁPIDO - Hoy mismo)
```
✅ Te creo el bot en 10 minutos
✅ Lo integro con la plataforma
✅ Puedes demostrar notificaciones funcionando
✅ Costo: $0
```

### Opción 2: WATI.io (PROFESIONAL - 1-2 días)
```
✅ Necesito que crees cuenta en wati.io
✅ Conectes tu WhatsApp Business
✅ Me des el API key
✅ Integro en 1 hora
✅ Costo: $49/mes
```

### Opción 3: Ambos (COMPLETO - 2 días)
```
✅ Telegram para demo inmediata
✅ WATI para producción
✅ Usuario elige su preferencia
✅ Costo: $49/mes (solo WATI)
```

---

## 🎯 PARA TWILIO (Si decides usarlo después)

**Te ayudo con:**
1. Llenar formulario de registro
2. Preparar documentos LOA
3. Configurar WhatsApp Business API
4. Integrar con backend

**Necesito de ti:**
- DNI/Pasaporte escaneado
- Dirección en España
- Número de teléfono para verificación
- Número WhatsApp Business (o te ayudo a crear uno)

---

## ❓ RESPONDE ESTO:

1. **¿Cuándo presentas a Orenes?**
2. **¿Prefieres Telegram (rápido) o WATI (profesional) para la demo?**
3. **¿Tienes WhatsApp Business o uso personal?**
4. **¿Quieres que implemente Telegram ahora mismo mientras decides?**

Con Telegram puedes tener notificaciones funcionando en **10 minutos** y demostrar el flujo completo en la presentación. 🚀
