import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ArrowLeft, Send, Bot, User, Sparkles, Lightbulb, Mic, MicOff, Phone } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';
import ReactMarkdown from 'react-markdown';
import { useElevenLabs } from '@/hooks/useElevenLabs';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CoachIAPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [mensaje, setMensaje] = useState('');
  const [conversacion, setConversacion] = useState([]);
  const [loading, setLoading] = useState(false);
  const [grabando, setGrabando] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const {
    toggleSession: toggleElevenLabs,
    isSessionActive: isElevenLabsActive,
    isSpeaking: isUserSpeaking,
    isAISpeaking
  } = useElevenLabs();

  const casosUso = [
    'Cómo mejorar mi comunicación con el equipo',
    'Estrategias para dar feedback constructivo',
    'Gestionar conflictos en el equipo',
    'Desarrollar mi inteligencia emocional'
  ];

  const handleEnviar = async () => {
    if (!mensaje.trim()) return;

    const nuevoMensaje = { role: 'user', content: mensaje };
    setConversacion([...conversacion, nuevoMensaje]);
    setMensaje('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/coach/consultar`, {
        mensaje,
        contexto: user?.cargo
      });
      
      const respuestaIA = { role: 'assistant', content: response.data.respuesta };
      setConversacion(prev => [...prev, respuestaIA]);
    } catch (error) {
      toast.error('Error al consultar el coach');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCasoUso = (caso) => {
    setMensaje(caso);
  };

  const iniciarGrabacion = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await enviarAudio(audioBlob);
        
        // Detener el stream
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setGrabando(true);
      toast.success('Grabando audio... 🎤');
    } catch (error) {
      console.error('Error al acceder al micrófono:', error);
      toast.error('No se pudo acceder al micrófono');
    }
  };

  const detenerGrabacion = () => {
    if (mediaRecorderRef.current && grabando) {
      mediaRecorderRef.current.stop();
      setGrabando(false);
    }
  };

  const enviarAudio = async (audioBlob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.webm');
      formData.append('contexto', user?.cargo || '');

      const response = await axios.post(`${API_URL}/coach/audio`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const mensajeTranscrito = { role: 'user', content: `🎤 ${response.data.transcripcion}` };
      const respuestaIA = { role: 'assistant', content: response.data.respuesta };
      
      setConversacion(prev => [...prev, mensajeTranscrito, respuestaIA]);
      toast.success('Audio procesado exitosamente');
    } catch (error) {
      toast.error('Error al procesar el audio');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleLlamarCoach = async () => {
    if (!phoneNumber.trim()) {
      toast.error('Por favor ingresa tu número de teléfono');
      return;
    }

    if (!phoneNumber.startsWith('+')) {
      toast.error('El número debe estar en formato internacional (ej: +34612345678)');
      return;
    }

    setLoadingCall(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/coach/llamar-vapi?phone_number=${encodeURIComponent(phoneNumber)}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('¡Llamada iniciada! Recibirás una llamada en breve 📞');
      
      // Limpiar campo
      setPhoneNumber('');
      
      // Agregar a conversación
      const mensajeLlamada = {
        role: 'system',
        content: `📞 Llamada de voz iniciada al número ${phoneNumber}`
      };
      setConversacion(prev => [...prev, mensajeLlamada]);
      
    } catch (error) {
      console.error('Error iniciando llamada:', error);
      const errorMsg = error.response?.data?.detail || 'Error al iniciar llamada';
      toast.error(errorMsg);
    } finally {
      setLoadingCall(false);
    }
  };

  const handleVoiceWeb = async () => {
    try {
      if (!vapiAssistantId) {
        toast.error('Configuración de VAPI no disponible');
        return;
      }

      if (isSessionActive) {
        stop();
        toast.info('Conversación de voz finalizada');
      } else {
        await start(vapiAssistantId);
        toast.success('🎙️ Conversación de voz iniciada. ¡Habla ahora!');
      }
    } catch (error) {
      console.error('Error con VAPI Web:', error);
      toast.error('Error al iniciar conversación de voz');
    }
  };

  return (
    <div className="min-h-screen bg-[#0A1628]">
      {/* Header */}
      <header className="bg-[#132337] border-b border-[#2D3748] sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} data-testid="btn-back">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-900 to-amber-500 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Coach IA</h1>
                <p className="text-sm text-gray-400">Tu asistente de liderazgo personalizado</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Info Card con botón Llamar */}
        <Card className="mb-8 bg-gradient-to-r from-green-700 to-green-500 text-white border-0 shadow-xl">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="w-6 h-6" />
                  <span>Tu Coach IA está aquí para ayudarte</span>
                </CardTitle>
                <CardDescription className="text-green-100">
                  Consulta por texto o llama para una sesión de voz
                </CardDescription>
              </div>
              <Button 
                variant="secondary"
                size="lg"
                className="bg-white text-green-700 hover:bg-green-50 font-semibold"
                onClick={() => toast.info('Función de llamadas próximamente disponible')}
                data-testid="btn-llamar-coach"
              >
                📞 Llamar a mi Coach
              </Button>
            </div>
          </CardHeader>
        </Card>

        {/* ElevenLabs - Hablar con el Coach */}
        <Card className="mb-8 bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-purple-200">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-slate-900">
              <Mic className="w-5 h-5 text-purple-600" />
              <span>🎙️ Hablar con mi Coach (Voz)</span>
              <span className="text-xs bg-green-600 text-white px-2 py-1 rounded-full ml-2">Nuevo</span>
            </CardTitle>
            <CardDescription>
              Conversación de voz en tiempo real. Habla naturalmente y el coach te responde como Euge Oller.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={toggleElevenLabs}
              className={`w-full ${
                isElevenLabsActive
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-purple-600 hover:bg-purple-700'
              } text-white py-6 text-lg font-semibold transition-all`}
            >
              {isElevenLabsActive ? (
                <>
                  <PhoneCall className="w-5 h-5 mr-2 animate-pulse" />
                  {isUserSpeakingEL ? '🗣️ Hablando...' : isAISpeakingEL ? '🎧 Coach hablando...' : '🎙️ En conversación - Click para finalizar'}
                </>
              ) : (
                <>
                  <Mic className="w-5 h-5 mr-2" />
                  🎙️ Iniciar conversación de voz
                </>
              )}
            </Button>
            {isElevenLabsActive && (
              <div className={`mt-3 p-3 rounded-lg border ${
                isUserSpeakingEL ? 'bg-blue-100 border-blue-300' :
                isAISpeakingEL ? 'bg-green-100 border-green-300' :
                'bg-purple-100 border-purple-200'
              }`}>
                <p className={`text-sm font-medium text-center ${
                  isUserSpeakingEL ? 'text-blue-900' :
                  isAISpeakingEL ? 'text-green-900' :
                  'text-purple-900'
                }`}>
                  {isUserSpeakingEL ? '🗣️ Te estoy escuchando...' : 
                   isAISpeakingEL ? '🎧 El Coach está respondiendo...' : 
                   '🎙️ Conversación activa - Puedes hablar cuando quieras'}
                </p>
              </div>
            )}
            <p className="text-xs text-gray-600 text-center mt-3">
              ✨ Conversación natural como con Euge Oller
            </p>
          </CardContent>
        </Card>

        {/* VAPI - Llamadas telefónicas (Próximamente) */}
        <Card className="mb-8 bg-gradient-to-br from-gray-50 to-gray-100 border-2 border-gray-200 opacity-60">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-slate-900">
              <Phone className="w-5 h-5 text-gray-600" />
              <span>Llamadas Telefónicas</span>
              <span className="text-xs bg-amber-500 text-white px-2 py-1 rounded-full ml-2">Próximamente</span>
            </CardTitle>
            <CardDescription>
              Recibe una llamada directamente en tu móvil. Disponible próximamente para España.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              disabled
              className="w-full bg-gray-400 text-white py-4 cursor-not-allowed"
            >
              <Phone className="w-4 h-4 mr-2" />
              Próximamente disponible
            </Button>
            <p className="text-xs text-gray-500 text-center mt-2">
              Mientras tanto, usa la conversación de voz en el navegador (arriba)
            </p>
          </CardContent>
        </Card>

        {/* Casos de Uso */}
        {conversacion.length === 0 && (
          <Card className="mb-8 border-2 border-slate-100">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-slate-900">
                <Lightbulb className="w-5 h-5 text-amber-500" />
                <span>Temas sugeridos</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 gap-3">
                {casosUso.map((caso, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="h-auto py-3 text-left justify-start hover:bg-blue-50 hover:border-blue-300"
                    onClick={() => handleCasoUso(caso)}
                    data-testid={`caso-uso-${index}`}
                  >
                    {caso}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Conversación */}
        <div className="space-y-4 mb-24" data-testid="conversacion-container">
          {conversacion.map((msg, index) => (
            <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
              <div className={`flex items-start space-x-3 max-w-2xl ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <Avatar className="flex-shrink-0">
                  <AvatarFallback className={msg.role === 'user' ? 'bg-blue-900 text-white' : 'bg-gradient-to-br from-amber-500 to-amber-600 text-white'}>
                    {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                  </AvatarFallback>
                </Avatar>
                <Card className={`${msg.role === 'user' ? 'bg-blue-900 text-white border-blue-800' : 'bg-white border-slate-200'}`}>
                  <CardContent className="py-3 px-4">
                    {msg.role === 'user' ? (
                      <p className="text-sm leading-relaxed text-white">
                        {msg.content}
                      </p>
                    ) : (
                      <div className="text-sm leading-relaxed text-slate-700 markdown-content">
                        <ReactMarkdown
                          components={{
                            // Custom styling for markdown elements
                            p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                            strong: ({node, ...props}) => <strong className="font-semibold text-slate-900" {...props} />,
                            ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-1 my-2" {...props} />,
                            li: ({node, ...props}) => <li className="ml-2" {...props} />,
                            h3: ({node, ...props}) => <h3 className="font-semibold text-base mt-2 mb-1" {...props} />,
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start animate-fade-in">
              <div className="flex items-start space-x-3 max-w-2xl">
                <Avatar className="flex-shrink-0">
                  <AvatarFallback className="bg-gradient-to-br from-amber-500 to-amber-600 text-white">
                    <Bot className="w-5 h-5" />
                  </AvatarFallback>
                </Avatar>
                <Card className="bg-white border-slate-200">
                  <CardContent className="py-3 px-4">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}
        </div>

        {/* Input Fijo */}
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 p-4 shadow-lg">
          <div className="container mx-auto max-w-4xl">
            {grabando && (
              <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between animate-pulse">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse" />
                  <span className="text-red-700 font-medium">Grabando audio...</span>
                </div>
                <Button 
                  onClick={detenerGrabacion}
                  className="bg-red-600 hover:bg-red-700 text-white"
                  size="sm"
                >
                  <MicOff className="w-4 h-4 mr-2" />
                  Detener y Enviar
                </Button>
              </div>
            )}
            <div className="flex space-x-3">
              <Input
                placeholder="Escribe tu consulta aquí..."
                value={mensaje}
                onChange={(e) => setMensaje(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleEnviar()}
                className="flex-1"
                disabled={loading || grabando}
                data-testid="input-mensaje"
              />
              {!grabando && (
                <Button 
                  onClick={iniciarGrabacion}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 text-white"
                  data-testid="btn-audio"
                  title="Grabar mensaje de voz"
                >
                  <Mic className="w-5 h-5" />
                </Button>
              )}
              <Button 
                onClick={handleEnviar}
                disabled={loading || !mensaje.trim() || grabando}
                className="bg-blue-900 hover:bg-blue-800"
                data-testid="btn-enviar"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoachIAPage;