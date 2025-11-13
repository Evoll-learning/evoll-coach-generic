import { useState, useEffect, useRef } from 'react';
import { Conversation } from '@11labs/client';

export const useElevenLabs = () => {
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const conversationRef = useRef(null);
  const isStartingRef = useRef(false);

  const start = async () => {
    // Prevenir múltiples inicializaciones simultáneas
    if (isStartingRef.current) {
      console.log('⚠️ Ya hay una sesión iniciándose...');
      return false;
    }

    // Si ya hay una sesión activa, no iniciar otra
    if (conversationRef.current) {
      console.log('⚠️ Ya hay una sesión activa');
      return false;
    }

    try {
      isStartingRef.current = true;
      console.log('🚀 Iniciando ElevenLabs Conversational AI...');

      const apiKey = process.env.REACT_APP_ELEVENLABS_API_KEY;
      const agentId = process.env.REACT_APP_ELEVENLABS_AGENT_ID || 'agent_7001k9s8hn8ffc0sfepa6nh516wm';

      if (!apiKey) {
        throw new Error('ElevenLabs API key no configurada');
      }

      console.log('🔑 Usando Agent ID:', agentId);

      // Inicializar conversación
      const conversation = await Conversation.startSession({
        agentId: agentId,
        apiKey: apiKey,
        onConnect: () => {
          console.log('✅ Conectado a ElevenLabs');
          setIsSessionActive(true);
        },
        onDisconnect: () => {
          console.log('📞 Desconectado de ElevenLabs');
          console.warn('⚠️ La sesión se desconectó. Esto puede deberse a:');
          console.warn('   1. Falta de crédito en ElevenLabs');
          console.warn('   2. Timeout del servidor');
          console.warn('   3. Problema de red');
          setIsSessionActive(false);
          setIsSpeaking(false);
          setIsAISpeaking(false);
          conversationRef.current = null;
        },
        onMessage: (message) => {
          console.log('📨 Mensaje:', message);
        },
        onError: (error) => {
          console.error('❌ Error ElevenLabs:', error);
          console.error('Detalles del error:', {
            message: error.message,
            code: error.code,
            type: error.type
          });
          
          // Mostrar alerta al usuario
          alert(`Error en conversación de voz: ${error.message || 'Error desconocido'}. La sesión se ha cerrado.`);
          
          setIsSessionActive(false);
          conversationRef.current = null;
        },
        onModeChange: (mode) => {
          console.log('🔄 Modo cambió a:', mode);
          
          if (mode.mode === 'speaking') {
            console.log('🗣️ Usuario hablando');
            setIsSpeaking(true);
            setIsAISpeaking(false);
          } else if (mode.mode === 'listening') {
            console.log('🎧 IA hablando');
            setIsSpeaking(false);
            setIsAISpeaking(true);
          } else {
            setIsSpeaking(false);
            setIsAISpeaking(false);
          }
        },
      });

      conversationRef.current = conversation;
      console.log('✅ Sesión de ElevenLabs iniciada correctamente');
      return true;

    } catch (error) {
      console.error('❌ Error iniciando ElevenLabs:', error);
      conversationRef.current = null;
      setIsSessionActive(false);
      return false;
    } finally {
      isStartingRef.current = false;
    }
  };

  const stop = async () => {
    console.log('🛑 Deteniendo sesión ElevenLabs...');

    if (conversationRef.current) {
      try {
        await conversationRef.current.endSession();
        console.log('✅ Sesión terminada correctamente');
      } catch (error) {
        console.error('⚠️ Error cerrando sesión:', error);
      }
      conversationRef.current = null;
    }

    setIsSessionActive(false);
    setIsSpeaking(false);
    setIsAISpeaking(false);
    isStartingRef.current = false;
  };

  const toggleSession = async () => {
    if (isSessionActive) {
      await stop();
    } else {
      await start();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (conversationRef.current) {
        console.log('🧹 Limpiando sesión al desmontar componente');
        try {
          conversationRef.current.endSession();
        } catch (error) {
          console.error('Error en cleanup:', error);
        }
      }
    };
  }, []);

  return {
    start,
    stop,
    toggleSession,
    isSessionActive,
    isSpeaking,
    isAISpeaking,
  };
};
