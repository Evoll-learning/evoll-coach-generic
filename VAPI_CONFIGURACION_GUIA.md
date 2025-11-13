# 📞 CONFIGURACIÓN DE VAPI - PASO A PASO

## IMPORTANTE: Sigue estos pasos EXACTAMENTE

---

## PASO 1: Acceder al Dashboard

1. Ve a: **https://dashboard.vapi.ai**
2. Login con tu cuenta
3. Deberías ver el dashboard principal

---

## PASO 2: Crear Assistant

1. Click en **"Assistants"** en el menú lateral izquierdo
2. Click en **"Create Assistant"** o **"+ New Assistant"**
3. Se abrirá un formulario de configuración

---

## PASO 3: Configuración Básica

**Sección: Basic Information**

- **Name:** `EvoLL Coach de Liderazgo`
- **Description:** `Coach ejecutivo experto en liderazgo para Grupo Orenes`

---

## PASO 4: Configuración del Modelo

**Sección: Model**

- **Provider:** OpenAI
- **Model:** `gpt-4o` o `gpt-4-turbo` (el más avanzado disponible)
- **Temperature:** `0.7` (para respuestas equilibradas)

---

## PASO 5: Configuración de Voz

**Sección: Voice**

- **Voice Provider:** Selecciona uno con voces en español
- **Voice:** Busca una voz en español de España, por ejemplo:
  - `es-ES-AlvaroNeural` (voz masculina)
  - `es-ES-ElviraNeural` (voz femenina)
- **Speed:** `1.0` (velocidad normal)

---

## PASO 6: First Message (Mensaje Inicial)

Copia y pega EXACTAMENTE esto:

```
Hola, soy tu Coach de Liderazgo de EvoLL para Grupo Orenes. Estoy aquí para ayudarte a desarrollar tus habilidades de liderazgo y gestión de equipos. ¿En qué puedo ayudarte hoy?
```

---

## PASO 7: System Prompt (CRÍTICO)

Copia y pega EXACTAMENTE esto:

```
Eres un coach ejecutivo experto en liderazgo trabajando con líderes de Grupo Orenes, una empresa familiar española con 56 años de experiencia en el sector del juego y entretenimiento.

INFORMACIÓN DEL USUARIO:
{{user_context}}

TU ROL:
- Ayudar a líderes a mejorar su comunicación con equipos
- Enseñar a dar y recibir feedback efectivo (upwards y downwards)
- Gestionar conflictos de forma constructiva
- Desarrollar inteligencia emocional
- Mejorar la toma de decisiones estratégicas
- Fortalecer habilidades de delegación

VALORES DE ORENES QUE DEBES REFORZAR:
- Experiencia: 56 años de trayectoria familiar
- Confianza y transparencia en todas las relaciones
- Compromiso genuino con las personas
- Sentimiento familiar y cercanía
- Generosidad y humildad

METODOLOGÍA:
1. Escucha activamente y haz preguntas poderosas
2. Sé empático pero directo cuando sea necesario
3. Ofrece consejos prácticos y accionables
4. Usa ejemplos concretos aplicables a su contexto
5. Conecta tus consejos con los valores de Orenes
6. Mantén conversaciones enfocadas en 2-3 minutos

ESTILO DE COMUNICACIÓN:
- Habla en español de España (tutea, no uses usted)
- Tono profesional pero cercano y cálido
- Respuestas concisas (máximo 100 palabras por respuesta)
- Usa pausas naturales para dar espacio a la reflexión
- Termina con una pregunta que invite a la acción

IMPORTANTE:
- NO des respuestas genéricas, personaliza según el contexto del usuario
- NO te extiendas demasiado, sé conciso y directo
- SI el usuario no tiene claro su pregunta, ayúdale a clarificarla
- SIEMPRE termina con un siguiente paso concreto

Recuerda: Eres un coach, no un consultor. Tu objetivo es que el líder encuentre sus propias respuestas, no darle todas las soluciones.
```

---

## PASO 8: Configuración Avanzada (Opcional pero Recomendado)

**Sección: Advanced Settings**

- **Max Duration:** `5 minutes` (duración máxima de la llamada)
- **End Call Message:** `Gracias por tu tiempo. Recuerda poner en práctica lo que hemos hablado. ¡Mucho éxito!`
- **Background Sound:** `office` o `none`

---

## PASO 9: Guardar Assistant

1. Click en **"Save"** o **"Create Assistant"**
2. Espera a que se guarde correctamente
3. Verás tu assistant en la lista

---

## PASO 10: COPIAR ASSISTANT ID (MUY IMPORTANTE)

1. En la lista de Assistants, encuentra el que acabas de crear
2. Click en el assistant para ver sus detalles
3. Busca el **"Assistant ID"** - se ve como: `asst_abc123xyz...`
4. **CÓPIALO COMPLETO**
5. **PÉGALO AQUÍ EN EL CHAT**

---

## PASO 11: Configurar en Backend

Una vez que me des el Assistant ID, yo lo configuraré en el backend ejecutando:

```bash
# Agregar a .env
echo 'VAPI_ASSISTANT_ID="asst_tu_id_aqui"' >> /app/backend/.env

# Reiniciar backend
sudo supervisorctl restart backend
```

---

## PASO 12: Probar la Llamada

1. Ve a: https://coach-ai-9.preview.emergentagent.com/coach-ia
2. Ingresa tu número de teléfono (formato: +34612345678)
3. Click en "Llamar"
4. Deberías recibir la llamada en 5-10 segundos
5. ¡Prueba la conversación!

---

## ❓ TROUBLESHOOTING

**Problema: No recibo la llamada**
- Verifica que tu número esté en formato internacional (+34...)
- Verifica que tengas saldo en tu cuenta VAPI
- Revisa los logs del backend: `tail -f /var/log/supervisor/backend.err.log`

**Problema: El assistant no habla español**
- Verifica que seleccionaste una voz es-ES
- Verifica el system prompt (debe estar en español)

**Problema: Respuestas demasiado largas**
- Ajusta el temperature a 0.5
- Edita el system prompt para enfatizar "conciso"

---

## 📊 COSTOS APROXIMADOS DE VAPI

- **Llamada de 2 minutos:** ~$0.10-0.15 USD
- **Llamada de 5 minutos:** ~$0.25-0.40 USD

**Incluye:** GPT-4 + síntesis de voz + telefonía

---

FIN DE LA GUÍA - ¿Ya tienes el Assistant ID?
