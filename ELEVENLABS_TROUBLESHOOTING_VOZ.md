# 🔧 TROUBLESHOOTING - PROBLEMAS DE VOZ ELEVENLABS

**Problemas reportados**:
1. Coach pregunta "¿Te has quedado callado?" cuando el usuario está hablando
2. Coach dice "Parece que no me oyes"
3. Volumen del coach baja solo durante la conversación
4. Conversación se corta inesperadamente

---

## 🎯 **CAUSA RAÍZ:**

Estos problemas son de **configuración del agente** en ElevenLabs, NO del código.

---

## ✅ **SOLUCIÓN - CONFIGURAR AGENTE EN ELEVENLABS:**

### **PASO 1: Ve al Dashboard de ElevenLabs**

1. https://elevenlabs.io/app/conversational-ai
2. Selecciona tu agente: `agent_7001k9s8hn8ffc0sfepa6nh516wm`
3. Click en "Edit" o "Settings"

---

### **PASO 2: Ajustar Configuración de Conversación**

Busca estas configuraciones y ajústalas:

#### **1. Voice Activity Detection (VAD)**

**Problema**: El agente piensa que te quedaste callado cuando estás hablando

**Solución**:
```
Silence Threshold: Aumentar a 2-3 segundos (no 0.5-1 segundo)
Speaking Threshold: Bajar sensibilidad a 0.3-0.4 (no 0.6-0.7)
```

Esto hace que el agente espere MÁS antes de pensar que terminaste de hablar.

#### **2. Timeout Settings**

**Problema**: La conversación se corta si hay silencio

**Solución**:
```
Max Silence Duration: Aumentar a 8-10 segundos (no 3-5 segundos)
Response Timeout: Aumentar a 15-20 segundos
```

Esto da más tiempo para reflexionar antes de responder.

#### **3. Audio Settings**

**Problema**: El volumen baja solo

**Solución**:
```
Auto Gain Control: DESACTIVAR
Volume Normalization: DESACTIVAR o Mantener en nivel fijo
Output Volume: Mantener en 100% fijo
```

Esto evita que el sistema ajuste el volumen automáticamente.

#### **4. Turn-Taking Behavior**

**Problema**: El agente interrumpe o pregunta si estás ahí

**Solución**:
```
Interruption Sensitivity: Bajar a "Low" o "Medium"
Wait for User: Aumentar a "High"
```

Esto hace que el agente sea más paciente.

---

### **PASO 3: Ajustar el Prompt del Agente**

Agrega estas instrucciones al inicio del prompt:

```
COMPORTAMIENTO DE CONVERSACIÓN:
- Si hay una pausa, espera al menos 3-4 segundos antes de preguntar si el usuario sigue ahí
- NO interrumpas si el usuario está reflexionando
- NO preguntes "¿sigues ahí?" a menos que hayan pasado más de 8 segundos de silencio total
- Si el usuario hace una pausa para pensar, asume que está procesando la información
- Mantén tu volumen constante durante toda la conversación
```

Ejemplo de prompt actualizado al inicio:

```
Eres un Coach Ejecutivo de Liderazgo experto para líderes corporativos españoles (Grupo Orenes).

COMPORTAMIENTO DE CONVERSACIÓN:
- Espera pacientemente cuando el usuario reflexiona (hasta 5 segundos)
- NO preguntes "¿sigues ahí?" o "¿te has quedado callado?" prematuramente
- Si hay silencio de más de 6-7 segundos, ENTONCES puedes preguntar educadamente
- Mantén volumen constante (no ajustes automáticamente)
- Permite pausas naturales para reflexión

[resto del prompt...]
```

---

## 🧪 **CONFIGURACIÓN RECOMENDADA COMPLETA:**

Para evitar TODOS los problemas, esta es la configuración ideal:

```yaml
Voice Activity Detection:
  - Silence Threshold: 2.5 segundos
  - Speaking Threshold: 0.35
  - Sensitivity: Medium-Low

Timeouts:
  - Max Silence Duration: 10 segundos
  - Response Timeout: 20 segundos
  - Inactivity Timeout: 30 segundos

Audio:
  - Auto Gain Control: OFF
  - Volume Normalization: OFF
  - Output Volume: 100% (fixed)
  - Echo Cancellation: ON
  - Noise Suppression: ON

Turn-Taking:
  - Interruption Sensitivity: Low
  - Wait for User: High
  - Allow Overlapping Speech: NO
```

---

## 🎯 **DÓNDE ENCONTRAR ESTAS CONFIGURACIONES:**

### **En el Dashboard de ElevenLabs:**

1. **Agent Settings** → **Voice Settings**:
   - Volume
   - Auto Gain Control
   - Noise Suppression

2. **Agent Settings** → **Conversation Behavior**:
   - Turn-Taking
   - Interruption Sensitivity
   - Silence Detection

3. **Agent Settings** → **Advanced**:
   - Timeouts
   - VAD Settings
   - Audio Processing

**Nota**: La ubicación exacta puede variar según la versión del dashboard.

---

## 🔍 **TROUBLESHOOTING ESPECÍFICO:**

### **Problema 1: "¿Te has quedado callado?"**

**Causa**: Silence Threshold muy bajo (ej: 0.5 segundos)

**Fix**:
1. Aumentar Silence Threshold a 2-3 segundos
2. Agregar al prompt: "NO preguntes si el usuario sigue ahí antes de 6 segundos"
3. Bajar Speaking Threshold a 0.3

### **Problema 2: "¿No me oyes?"**

**Causa**: El agente no detecta tu voz correctamente

**Fix**:
1. Bajar Speaking Threshold (hacer más sensible a tu voz)
2. Activar Noise Suppression
3. Verificar permisos de micrófono en el navegador
4. Probar con diferentes navegadores (Chrome funciona mejor)

### **Problema 3: Volumen baja solo**

**Causa**: Auto Gain Control activado

**Fix**:
1. DESACTIVAR Auto Gain Control
2. DESACTIVAR Volume Normalization
3. Fijar Output Volume en 100%
4. Verificar que el navegador no esté controlando el volumen

### **Problema 4: Conversación se corta**

**Causa**: Timeouts muy cortos

**Fix**:
1. Aumentar Max Silence Duration a 10 segundos
2. Aumentar Inactivity Timeout a 30 segundos
3. Aumentar Response Timeout a 20 segundos

---

## 🎬 **FLUJO DE PRUEBA DESPUÉS DE AJUSTAR:**

1. Guarda cambios en ElevenLabs dashboard
2. Espera 1-2 minutos para que se apliquen
3. Recarga la página de la app (Ctrl+Shift+R)
4. Inicia nueva conversación de voz
5. Prueba:
   - Hablar y hacer pausas largas (3-4 segundos)
   - Dejar silencio de 5-6 segundos
   - Verificar que el volumen se mantiene constante
   - Verificar que no interrumpe prematuramente

---

## 💡 **ALTERNATIVA SI NO ENCUENTRAS LAS CONFIGURACIONES:**

Si no encuentras estas configuraciones en el dashboard de ElevenLabs, puedes:

### **Opción A: Contactar Soporte de ElevenLabs**

Email: support@elevenlabs.io

Mensaje sugerido:
```
Hola,

Estoy usando el Conversational AI Agent (ID: agent_7001k9s8hn8ffc0sfepa6nh516wm).

Tengo los siguientes problemas:
1. El agente pregunta "¿sigues ahí?" muy rápido (antes de 2 segundos)
2. El volumen baja automáticamente durante la conversación
3. La conversación se corta con silencios de más de 3 segundos

¿Pueden ayudarme a ajustar:
- Silence Threshold a 2-3 segundos
- Desactivar Auto Gain Control
- Aumentar Max Silence Duration a 10 segundos?

Gracias!
```

### **Opción B: Solución Temporal en el Prompt**

Mientras ajustas la configuración, agrega al prompt:

```
INSTRUCCIONES CRÍTICAS DE CONVERSACIÓN:
1. NUNCA preguntes "¿sigues ahí?" o "¿te has quedado callado?" antes de 8 segundos de silencio total
2. Si el usuario hace una pausa de 3-5 segundos, asume que está reflexionando
3. Espera pacientemente sin interrumpir
4. Si después de 8 segundos no hay respuesta, entonces pregunta: "¿Necesitas más tiempo para reflexionar?"
5. Mantén un tono de voz constante y volumen estable durante toda la conversación
```

---

## 📊 **COMPARACIÓN: ANTES vs DESPUÉS**

| Configuración | ANTES (problemático) | DESPUÉS (ideal) |
|--------------|---------------------|-----------------|
| Silence Threshold | 0.5s | 2.5s |
| Speaking Threshold | 0.7 | 0.35 |
| Max Silence | 3s | 10s |
| Auto Gain | ON | OFF |
| Volume | Auto | Fixed 100% |
| Interrupciones | High | Low |

---

## ✅ **CHECKLIST DE CONFIGURACIÓN:**

- [ ] Silence Threshold aumentado a 2-3 segundos
- [ ] Speaking Threshold bajado a 0.3-0.4
- [ ] Max Silence Duration aumentado a 10 segundos
- [ ] Auto Gain Control DESACTIVADO
- [ ] Volume Normalization DESACTIVADO
- [ ] Output Volume fijado en 100%
- [ ] Interruption Sensitivity en "Low"
- [ ] Prompt actualizado con instrucciones de silencio
- [ ] Noise Suppression ACTIVADO
- [ ] Echo Cancellation ACTIVADO

---

## 🚨 **SI EL PROBLEMA PERSISTE:**

1. **Verifica tu micrófono**:
   - Probar en otra app (Zoom, Google Meet)
   - Verificar que no haya ruido de fondo
   - Hablar a distancia adecuada (15-30cm)

2. **Verifica tu navegador**:
   - Usar Chrome (mejor soporte)
   - Dar permisos completos de micrófono
   - Verificar que no haya extensiones bloqueando

3. **Verifica tu conexión**:
   - Conexión estable (no móvil 3G/4G)
   - Latencia baja (<100ms)
   - Speed test: https://www.speedtest.net/

4. **Considera plan de ElevenLabs**:
   - Plan gratuito puede tener limitaciones
   - Plan Pro tiene mejor calidad de conversación
   - Verifica límites de tu plan

---

## 📞 **RECURSOS:**

- ElevenLabs Docs: https://elevenlabs.io/docs
- Conversational AI Settings: https://elevenlabs.io/docs/conversational-ai/settings
- Support: support@elevenlabs.io

---

**Última actualización**: 11 Noviembre 2025  
**Versión**: 1.0 - Troubleshooting completo
