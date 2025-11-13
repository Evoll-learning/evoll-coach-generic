# 🔧 CONFIGURACIÓN DE NÚMERO DE TELÉFONO EN VAPI

## ⚠️ IMPORTANTE
Para que VAPI pueda hacer llamadas salientes, **NECESITAS UN NÚMERO DE TELÉFONO**. Sin esto, recibirás error 401 o llamadas fallidas.

---

## 🎯 OPCIÓN 1: COMPRAR NÚMERO DIRECTAMENTE EN VAPI (RECOMENDADO)

### Paso 1: Accede al Dashboard
1. Ve a: https://dashboard.vapi.ai
2. Login con tu cuenta

### Paso 2: Navega a Phone Numbers
1. En el menú lateral, busca **"Phone Numbers"** o **"Numbers"**
2. Haz clic en **"Buy Phone Number"** o **"Add Number"**

### Paso 3: Selecciona tu número
1. Elige **país**: España (+34)
2. Elige **área**: Madrid, Barcelona, etc (opcional)
3. Selecciona un número disponible
4. **Confirma la compra**

💰 **Costo aproximado**: 
- Compra inicial: ~$1-2 USD
- Mensual: ~$1 USD/mes
- Por minuto de llamada: ~$0.01-0.02 USD/min

### Paso 4: Asigna el número a tu Assistant
1. Ve a tu Assistant: `a929f25c-7e71-4ff1-815c-ead8108e8852`
2. En **Settings**, busca **"Phone Number"**
3. Selecciona el número que compraste
4. **Save changes**

### Paso 5: Verifica tu API Key
1. En dashboard, ve a **"API Keys"** o **"Settings"**
2. Copia tu **Private API Key** (debe empezar con algo como `sk-...` o similar)
3. **¡IMPORTANTE!** Usa la **Private Key**, NO la Public Key

---

## 🎯 OPCIÓN 2: USAR TWILIO (Si ya tienes cuenta)

Si ya tienes Twilio con números de teléfono configurados:

### Paso 1: Configura SIP Trunk en VAPI
1. Ve a VAPI Dashboard > **"Integrations"** o **"SIP Trunks"**
2. Haz clic en **"Add Twilio Integration"**

### Paso 2: Ingresa credenciales de Twilio
- **Account SID**: (de tu dashboard de Twilio)
- **Auth Token**: (de tu dashboard de Twilio)
- **Phone Number**: (tu número de Twilio en formato +34...)

### Paso 3: Prueba la conexión
- Haz una llamada de prueba desde VAPI
- Verifica que funcione correctamente

---

## 🔑 VERIFICAR TU API KEY CORRECTA

### Paso 1: Ve a VAPI Dashboard
https://dashboard.vapi.ai

### Paso 2: Encuentra tu API Key
1. Ve a **"Settings"** o **"API Keys"**
2. Busca tu **Private API Key**
3. Debe verse algo como:
   - `sk-abc123...` (formato típico)
   - `0067fab5-0e9f-4085-8277-a163f79a3215` (UUID format)

### Paso 3: Verifica que sea la PRIVATE KEY
- **Private Key**: Para backend (server-side) ✅ USAR ESTA
- **Public Key**: Para frontend (web widget) ❌ NO USAR

---

## 🧪 DESPUÉS DE CONFIGURAR

Una vez tengas tu número configurado y la API key correcta:

1. **Actualiza el .env** del backend:
```bash
VAPI_API_KEY="[tu_private_key_correcta]"
VAPI_ASSISTANT_ID="a929f25c-7e71-4ff1-815c-ead8108e8852"
VAPI_PHONE_NUMBER="+34612345678"  # El número que compraste
```

2. **Reinicia el backend**:
```bash
sudo supervisorctl restart backend
```

3. **Prueba desde la web**:
   - Ve a Coach IA
   - Ingresa TU número (+34...)
   - Click "Llamar"
   - Deberías recibir una llamada en ~10-30 segundos

---

## ❓ PREGUNTAS FRECUENTES

### ¿Cuánto cuesta?
- Número de teléfono: ~$1-2 USD compra + $1/mes
- Llamadas: ~$0.01-0.02 USD por minuto
- Total para pruebas: ~$5-10 USD

### ¿Puedo usar un número gratis?
No directamente. VAPI necesita números reales para llamar.

### ¿Funciona con números de otros países?
Sí, pero es mejor comprar un número del país donde están tus usuarios (España +34).

### ¿La llamada es instantánea?
No, puede tardar 10-30 segundos en iniciar la llamada.

---

## 🆘 SI SIGUES TENIENDO ERRORES

### Error 401: "Invalid Key"
- ✅ Verifica que uses **Private Key**, no Public Key
- ✅ Verifica que la key esté copiada correctamente (sin espacios)
- ✅ Genera una nueva key en el dashboard si es necesario

### Error: "No phone number configured"
- ✅ Compra un número en VAPI
- ✅ Asígnalo a tu Assistant
- ✅ Espera 1-2 minutos para que se propague

### La llamada no llega
- ✅ Verifica formato del número: +34612345678 (con código país)
- ✅ Verifica que tu teléfono pueda recibir llamadas
- ✅ Revisa logs del dashboard de VAPI

---

## 📞 SOPORTE

Si necesitas ayuda:
- VAPI Community: https://vapi.ai/community
- VAPI Docs: https://docs.vapi.ai
- Support: support@vapi.ai

---

FIN DEL DOCUMENTO
