# 🔧 FIX APLICADO - ELEVENLABS "SE PARA"

**Problema reportado**: Coach dice "Hola soy tu coach de liderazgo" y se para

---

## ✅ **SOLUCIÓN APLICADA:**

### **Causa del problema:**
- ElevenLabs necesita la API key en el frontend (client-side)
- La API key estaba solo en el backend
- El hook `useElevenLabs.js` no la estaba enviando

### **Fix implementado:**

1. ✅ Agregada API key en `/app/frontend/.env`:
   ```env
   REACT_APP_ELEVENLABS_API_KEY=sk_242a1dbaceb5c2207d5b96fdf7fca08012a09455f5936bb4
   ```

2. ✅ Actualizado `/app/frontend/src/hooks/useElevenLabs.js`:
   - Ahora lee la API key de las variables de entorno
   - La pasa a `Conversation.startSession()`
   - Agregado logging para debug

3. ✅ Frontend reiniciado para cargar las nuevas variables

---

## 🧪 **CÓMO PROBAR:**

### **Paso 1**: Ve a Coach IA
1. Login con julio@evoll.es / test123
2. Click en "Coach IA" en el menú

### **Paso 2**: Inicia conversación de voz
1. Click en el botón morado "🎙️ Iniciar conversación de voz"
2. Permite acceso al micrófono si te lo pide el navegador
3. Espera unos segundos

### **Paso 3**: Verifica que funciona
- Deberías ver: "🎙️ En conversación - Click para finalizar"
- El coach debería decir su mensaje de bienvenida COMPLETO
- Deberías poder hablar y recibir respuestas

### **Paso 4**: Revisa la consola del navegador (F12)
Deberías ver logs como:
```
🚀 Iniciando ElevenLabs Conversational AI...
🔑 Usando API Key y Agent ID: { agentId: 'agent_7001k9s8hn8ffc0sfepa6nh516wm' }
✅ Conectado a ElevenLabs
```

---

## ❌ **SI SIGUE SIN FUNCIONAR:**

### **Opción A: Problema de API Key**
```bash
# Verifica que la API key sea válida en ElevenLabs dashboard
# Si expirió o está inactiva, necesitarás una nueva
```

### **Opción B: Problema del Agente**
1. Ve a: https://elevenlabs.io/app/conversational-ai
2. Verifica que el agente `agent_7001k9s8hn8ffc0sfepa6nh516wm` exista
3. Verifica que esté activo (no en draft)
4. Verifica que tenga el prompt actualizado

### **Opción C: Problema de permisos de micrófono**
- Verifica que el navegador tenga permisos de micrófono
- Intenta en Chrome (funciona mejor que otros navegadores)
- Verifica que no haya otras apps usando el micrófono

---

## 🔍 **DEBUGGING:**

### **Ver logs del frontend:**
```bash
# En el servidor
tail -f /var/log/supervisor/frontend.err.log
```

### **Ver logs del navegador:**
1. Abre la consola del navegador (F12)
2. Ve a la pestaña "Console"
3. Busca mensajes de "ElevenLabs" o errores en rojo

### **Errores comunes:**

**Error: "API key no configurada"**
- Solución: Ya está configurada ahora, recarga la página

**Error: "Permission denied"**
- Solución: Da permisos de micrófono al navegador

**Error: "Agent not found"**
- Solución: Verifica que el agente existe en tu dashboard de ElevenLabs

**Error: "Quota exceeded"**
- Solución: Tu plan de ElevenLabs puede haber llegado al límite

---

## 📝 **ARCHIVOS MODIFICADOS:**

1. `/app/frontend/.env` - Agregada API key
2. `/app/frontend/src/hooks/useElevenLabs.js` - Agregada lógica para usar API key
3. Frontend reiniciado

---

## ✅ **VERIFICACIÓN RÁPIDA:**

```bash
# 1. Verificar que la variable está en .env
grep ELEVENLABS /app/frontend/.env

# 2. Verificar que el hook tiene el código nuevo
grep "apiKey" /app/frontend/src/hooks/useElevenLabs.js

# 3. Verificar que el frontend está corriendo
sudo supervisorctl status frontend
```

---

## 🚨 **IMPORTANTE:**

Después de este fix:
1. **Recarga la página** en el navegador (Ctrl+Shift+R o Cmd+Shift+R)
2. **Prueba la conversación de voz**
3. **Si funciona**: ¡Perfecto! Ya puedes actualizar el prompt en ElevenLabs
4. **Si no funciona**: Revisa los logs y cuéntame el error exacto

---

## 📞 **PRÓXIMOS PASOS:**

Una vez que funcione:
1. ✅ Actualiza el prompt en ElevenLabs con `ELEVENLABS_PROMPT_FINAL.md`
2. ✅ Prueba 2-3 conversaciones para verificar el nuevo comportamiento
3. ✅ Muestra a RRHH los ejemplos de `EJEMPLOS_CONVERSACIONES_COACH.md`
4. 🚀 Deploy en Railway cuando estés listo

---

**Estado**: Fix aplicado, pendiente de prueba por usuario

**Última actualización**: 11 Noviembre 2025 - 19:40
