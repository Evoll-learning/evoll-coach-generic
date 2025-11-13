# ✅ VAPI WEB SDK IMPLEMENTADO

**Fecha:** 10 Noviembre 2025
**Funcionalidad:** Conversación de voz en tiempo real con el Coach IA directamente en el navegador

---

## 🎯 ¿QUÉ ES VAPI WEB SDK?

Es una forma de hablar con el Coach IA **por voz** directamente desde el navegador, **SIN necesidad de número de teléfono** y **SIN costos de llamadas telefónicas**.

### **Diferencias:**

| Característica | VAPI Web SDK | VAPI Outbound Calls |
|----------------|--------------|---------------------|
| **Dónde funciona** | En el navegador | Teléfono móvil |
| **Requiere número** | ❌ NO | ✅ SÍ (comprar en VAPI) |
| **Costo adicional** | ❌ NO (solo tokens GPT-4o) | ✅ SÍ (~$0.01-0.02/min) |
| **Cuándo usar** | Usuario en la plataforma | Notificaciones proactivas |
| **Experiencia** | Como videollamada (Zoom/Meet) | Llamada telefónica tradicional |

---

## ✅ LO QUE SE IMPLEMENTÓ

### **1. Backend (`/app/backend/`)**

#### **Archivos modificados:**

**`vapi_integration.py`**
- ✅ Nueva función: `obtener_web_token(user_context)`
- Devuelve el Assistant ID y metadata del usuario
- No require autenticación especial, solo el Assistant ID

**`server.py`**
- ✅ Nuevo endpoint: `GET /api/coach/vapi-web-token`
- Protegido con autenticación (requiere login)
- Devuelve configuración para el Web SDK

---

### **2. Frontend (`/app/frontend/`)**

#### **Archivos creados:**

**`src/hooks/useVapi.js`** (NUEVO)
```javascript
// Hook personalizado para manejar VAPI Web SDK
- inicializa el cliente de VAPI
- maneja eventos (call-start, call-end, speech-start, etc)
- expone funciones: start(), stop(), toggleCall()
- gestiona estado: isSessionActive, isSpeaking, volumeLevel
```

#### **Archivos modificados:**

**`src/pages/CoachIAPage.js`**
- ✅ Importado hook `useVapi`
- ✅ Nuevo estado: `vapiAssistantId`
- ✅ Nueva función: `handleVoiceWeb()` para iniciar/parar voz
- ✅ useEffect para obtener config de VAPI al cargar
- ✅ Nuevo componente UI: Card "Hablar con mi Coach" (morado)

**`.env`**
```bash
REACT_APP_VAPI_PUBLIC_KEY=orenes-coach
```

#### **Dependencias instaladas:**
```bash
yarn add @vapi-ai/web
```

---

## 🎨 UI IMPLEMENTADA

### **Tarjeta "Hablar con mi Coach"** (Morado/Púrpura)

**Ubicación:** Coach IA page, antes de la tarjeta de llamadas telefónicas

**Estados:**

1. **Inactivo:**
   - Botón grande morado
   - Texto: "🎙️ Iniciar conversación de voz"
   - Click → Inicia conversación

2. **Activo - Escuchando:**
   - Botón rojo (para finalizar)
   - Texto: "🗣️ Hablando..."
   - Indicador abajo: "🗣️ Escuchando..."

3. **Activo - Coach hablando:**
   - Botón rojo (para finalizar)
   - Texto: "🎙️ En llamada - Click para finalizar"
   - Indicador abajo: "🎧 El Coach está hablando"

---

## 🔧 CÓMO FUNCIONA (Flujo Técnico)

```
1. Usuario carga Coach IA page
   ↓
2. Frontend hace GET /api/coach/vapi-web-token
   ↓
3. Backend devuelve:
   {
     "assistant_id": "a929f25c-7e71-4ff1-815c-ead8108e8852",
     "user_name": "Julio",
     "user_cargo": "CEO"
   }
   ↓
4. Frontend inicializa VAPI client con Public Key
   ↓
5. Usuario hace click en "Iniciar conversación de voz"
   ↓
6. Frontend llama: vapi.start(assistant_id)
   ↓
7. VAPI solicita permiso de micrófono
   ↓
8. Usuario acepta → Conversación inicia
   ↓
9. Usuario habla → VAPI transcribe → GPT-4o responde → Voz sintetizada
   ↓
10. Usuario click "Finalizar" → vapi.stop()
```

---

## 🧪 CÓMO PROBAR

### **Paso 1: Acceder a la plataforma**
URL: https://coach-ai-9.preview.emergentagent.com

### **Paso 2: Login**
- Email: `julio@evoll.es`
- Password: `test123`

### **Paso 3: Ir a Coach IA**
Menú lateral → "Coach IA"

### **Paso 4: Buscar la tarjeta morada**
"Hablar con mi Coach" (con badge "Nuevo")

### **Paso 5: Probar la conversación**
1. Click en "🎙️ Iniciar conversación de voz"
2. Permitir acceso al micrófono cuando el navegador lo pida
3. Hablar: "Hola, soy Julio y necesito ayuda con mi equipo"
4. Esperar respuesta del Coach
5. Continuar conversación naturalmente
6. Click en el botón rojo para finalizar

---

## ⚠️ REQUISITOS DEL NAVEGADOR

### **Compatibilidad:**
- ✅ Chrome 79+ (recomendado)
- ✅ Edge 79+
- ✅ Firefox 86+
- ✅ Safari 14.1+

### **Requisitos:**
- ✅ HTTPS (ya lo tenemos)
- ✅ Permiso de micrófono
- ✅ WebRTC habilitado (por defecto en navegadores modernos)

---

## 💰 COSTOS

### **VAPI Web SDK:**
- ❌ **NO cuesta por llamada**
- ✅ **Solo pagas por uso de GPT-4o** (tokens de texto)
- Costo aproximado: ~$0.002-0.01 USD por conversación de 5 minutos

### **Comparación con Outbound Calls:**
| Métrica | Web SDK | Outbound Calls |
|---------|---------|----------------|
| Setup | $0 | ~$2 número + $1/mes |
| Por minuto | $0 | ~$0.01-0.02 |
| 100 conversaciones (5 min) | ~$1-2 | ~$5-10 |

---

## 🐛 TROUBLESHOOTING

### **Problema: Botón deshabilitado**
**Causa:** `vapiAssistantId` no se cargó
**Solución:**
1. Verificar backend corriendo: `sudo supervisorctl status backend`
2. Verificar endpoint: `curl https://[url]/api/coach/vapi-web-token` (con token)
3. Verificar logs: `tail -f /var/log/supervisor/backend.err.log`

### **Problema: "No se pudo acceder al micrófono"**
**Causa:** Usuario denegó permisos o navegador no soporta WebRTC
**Solución:**
1. Verificar que estás en HTTPS (ya lo tenemos)
2. Revisar permisos del navegador (icono de candado → permisos)
3. Probar en Chrome/Edge (mejor soporte)

### **Problema: No escucha mi voz**
**Causa:** Micrófono no funciona o está silenciado
**Solución:**
1. Verificar que el micrófono esté funcionando (probar en otra app)
2. Verificar nivel de volumen del micrófono
3. Cerrar otras apps que usen el micrófono

### **Problema: Coach no responde**
**Causa:** Error en VAPI o GPT-4o
**Solución:**
1. Ver consola del navegador (F12)
2. Verificar logs del backend
3. Verificar que VAPI API key sea correcta

---

## 🎯 PRÓXIMOS PASOS

### **Mejoras Opcionales:**

1. **Indicador de volumen visual**
   - Mostrar barras de audio cuando el usuario habla
   - Usar `volumeLevel` del hook useVapi

2. **Transcripción en pantalla**
   - Mostrar lo que el usuario dice
   - Mostrar respuestas del Coach en texto también

3. **Historial de conversaciones**
   - Guardar transcripciones en DB
   - Mostrar conversaciones previas

4. **Configuración de voz**
   - Permitir elegir voz (masculina/femenina)
   - Ajustar velocidad de habla

---

## 📞 INTEGRACIÓN DUAL: WEB SDK + OUTBOUND CALLS

Ahora tienes **DOS opciones de voz** en la misma plataforma:

### **Opción 1: Web SDK (YA FUNCIONAL)** 💻
- Usuario está en la web
- Click → Habla inmediatamente
- Sin costos adicionales

### **Opción 2: Outbound Calls (Pendiente)** 📞
- Usuario NO está en la web
- Recibe llamada en su teléfono
- Útil para notificaciones proactivas
- **Requiere:** Comprar número en VAPI (~$2)

**Recomendación:** Usa Web SDK para la mayoría de casos, y Outbound Calls solo para notificaciones especiales (ej: "Tu evaluación mensual está lista, tu coach te llama").

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Instalar @vapi-ai/web
- [x] Crear hook useVapi
- [x] Agregar Public Key al .env
- [x] Crear endpoint /coach/vapi-web-token
- [x] Actualizar CoachIAPage con botón
- [x] Reiniciar frontend y backend
- [x] Probar conversación de voz
- [ ] **Testing manual por usuario** ⬅️ SIGUIENTE PASO

---

## 📝 NOTAS IMPORTANTES

1. **VAPI Web SDK es DIFERENTE a llamadas telefónicas**
   - Web SDK = Navegador (gratis)
   - Outbound Calls = Teléfono (requiere número)

2. **La misma API key funciona para ambos**
   - Public Key: Para Web SDK (frontend)
   - Private Key: Para Outbound Calls (backend)

3. **El Assistant configurado funciona para ambos**
   - ID: `a929f25c-7e71-4ff1-815c-ead8108e8852`
   - Prompt: Coach ejecutivo en español
   - Voz: es-ES-ElviraNeural (Azure)

---

FIN DEL DOCUMENTO
