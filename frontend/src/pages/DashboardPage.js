import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  CircularProgress, 
  HorizontalMetricBar, 
  DistributionPieChart 
} from '@/components/DashboardCharts';
import { 
  LayoutDashboard, 
  MessageSquare, 
  Users, 
  Brain, 
  User, 
  LogOut, 
  TrendingUp,
  Calendar,
  CheckCircle,
  Clock,
  Send,
  Sparkles,
  Award,
  Target,
  Zap,
  Mic,
  MicOff
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('resumen');
  const [metricas, setMetricas] = useState(null);
  const [preguntaDia, setPreguntaDia] = useState(null);
  const [respuestaTexto, setRespuestaTexto] = useState('');
  const [misRespuestas, setMisRespuestas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);
  const [userStats, setUserStats] = useState(null);
  const [badges, setBadges] = useState([]);
  const [grabando, setGrabando] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    console.log('🚀 Dashboard mounted - fetching all data...');
    fetchMetricas();
    fetchPreguntaDia();
    fetchMisRespuestas();
    fetchLeaderboard();
    fetchUserStats();
    fetchBadges();
    
    // Detectar si viene desde Telegram con hash #lmv
    if (window.location.hash === '#lmv') {
      setActiveTab('lmv');
      // Limpiar el hash de la URL
      window.history.replaceState(null, '', window.location.pathname);
    }
  }, []);
  
  // Log cuando cambie misRespuestas
  useEffect(() => {
    console.log('📊 misRespuestas state changed:', misRespuestas);
    console.log('📏 Length:', misRespuestas.length);
  }, [misRespuestas]);

  const fetchMetricas = async () => {
    try {
      const response = await axios.get(`${API_URL}/metricas/progreso`);
      setMetricas(response.data);
    } catch (error) {
      console.error('Error fetching metricas:', error);
    }
  };

  const fetchPreguntaDia = async () => {
    try {
      const response = await axios.get(`${API_URL}/lmv/pregunta-dia`);
      setPreguntaDia(response.data);
    } catch (error) {
      console.error('Error fetching pregunta:', error);
    }
  };

  const fetchMisRespuestas = async () => {
    try {
      console.log('🔍 Fetching mis respuestas from:', `${API_URL}/lmv/mis-respuestas`);
      const response = await axios.get(`${API_URL}/lmv/mis-respuestas`);
      console.log('✅ Response received:', response);
      console.log('📊 Response data:', response.data);
      console.log('📏 Array length:', response.data?.length);
      
      if (Array.isArray(response.data)) {
        console.log(`✅ Setting ${response.data.length} respuestas to state`);
        setMisRespuestas(response.data);
      } else {
        console.error('❌ Response is not an array:', typeof response.data);
        setMisRespuestas([]);
      }
    } catch (error) {
      console.error('❌ Error fetching respuestas:', error);
      console.error('Error details:', error.response?.data);
    }
  };

  const handleResponder = async () => {
    if (!respuestaTexto.trim()) {
      toast.error('Por favor escribe tu respuesta');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_URL}/lmv/responder`, {
        pregunta: preguntaDia.pregunta,
        respuesta_texto: respuestaTexto
      });
      toast.success('¡Respuesta enviada exitosamente!');
      setRespuestaTexto('');
      fetchPreguntaDia();
      fetchMisRespuestas();
      fetchMetricas();
    } catch (error) {
      toast.error('Error al enviar respuesta');
    } finally {
      setLoading(false);
    }
  };

  const competencias = metricas ? [
    { nombre: 'Comunicación Efectiva', valor: metricas.comunicacion_efectiva, icon: MessageSquare, color: 'bg-blue-500' },
    { nombre: 'Feedback Constructivo', valor: metricas.feedback_constructivo, icon: TrendingUp, color: 'bg-green-500' },
    { nombre: 'Gestión de Conflictos', valor: metricas.gestion_conflictos, icon: Users, color: 'bg-amber-500' },
    { nombre: 'Delegación', valor: metricas.delegacion, icon: CheckCircle, color: 'bg-purple-500' },
    { nombre: 'Inteligencia Emocional', valor: metricas.inteligencia_emocional, icon: Brain, color: 'bg-pink-500' },
    { nombre: 'Pensamiento Estratégico', valor: metricas.pensamiento_estrategico, icon: Sparkles, color: 'bg-indigo-500' }
  ] : [];

  const fetchLeaderboard = async () => {
    try {
      const response = await axios.get(`${API_URL}/leaderboard`);
      setLeaderboard(response.data.leaderboard || []);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  const fetchUserStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserStats(response.data);
    } catch (error) {
      console.error('Error fetching user stats:', error);
    }
  };

  const fetchBadges = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/badges`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBadges(response.data.badges || []);
    } catch (error) {
      console.error('Error fetching badges:', error);
    }
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
    if (!preguntaDia) return;
    
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'respuesta.webm');
      formData.append('pregunta_id', preguntaDia.id || '');
      
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/respuestas/audio`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${token}`
          }
        }
      );

      toast.success('✅ Audio procesado y respuesta guardada (+10 pts)');
      
      // Limpiar y recargar
      setRespuestaTexto('');
      fetchPreguntaDia();
      fetchMisRespuestas();
      
    } catch (error) {
      console.error('Error enviando audio:', error);
      toast.error('Error al procesar el audio');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleGrabacion = () => {
    if (grabando) {
      detenerGrabacion();
    } else {
      iniciarGrabacion();
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#0A1628]">
      {/* Header */}
      <header className="bg-[#132337] border-b border-[#2D3748] sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-green-400 rounded-lg flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">EvoLL</h1>
                <p className="text-xs text-gray-400">Evoll AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-300">Hola, {user?.nombre}</span>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleLogout} 
                className="border-gray-600 hover:bg-gray-700 text-gray-300"
                data-testid="btn-logout"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        {/* Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="bg-[#132337] border border-[#2D3748] p-1">
            <TabsTrigger 
              value="resumen" 
              className="flex items-center space-x-2 data-[state=active]:bg-green-600 data-[state=active]:text-white text-gray-400" 
              data-testid="tab-resumen"
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Resumen</span>
            </TabsTrigger>
            <TabsTrigger 
              value="lmv" 
              className="flex items-center space-x-2 data-[state=active]:bg-green-600 data-[state=active]:text-white text-gray-400" 
              data-testid="tab-lmv"
            >
              <Calendar className="w-4 h-4" />
              <span>L-M-V</span>
            </TabsTrigger>
            <TabsTrigger 
              value="comunidad" 
              className="flex items-center space-x-2 data-[state=active]:bg-green-600 data-[state=active]:text-white text-gray-400" 
              onClick={() => navigate('/comunidad')} 
              data-testid="tab-comunidad"
            >
              <Users className="w-4 h-4" />
              <span>Comunidad</span>
            </TabsTrigger>
            <TabsTrigger 
              value="coach" 
              className="flex items-center space-x-2 data-[state=active]:bg-green-600 data-[state=active]:text-white text-gray-400" 
              onClick={() => navigate('/coach')} 
              data-testid="tab-coach"
            >
              <Brain className="w-4 h-4" />
              <span>Coach IA</span>
            </TabsTrigger>
            <TabsTrigger 
              value="perfil" 
              className="flex items-center space-x-2 data-[state=active]:bg-green-600 data-[state=active]:text-white text-gray-400" 
              onClick={() => navigate('/perfil')} 
              data-testid="tab-perfil"
            >
              <User className="w-4 h-4" />
              <span>Perfil</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="resumen" className="mt-6">
            <div className="space-y-6">
              {/* Header with Name and Title */}
              <div className="text-center mb-8">
                <h2 className="text-4xl font-bold text-white mb-2">{user?.nombre} {user?.apellido}</h2>
                <p className="text-xl text-green-400">Programa de Liderazgo Evolutivo</p>
                <div className="flex justify-center items-center space-x-4 mt-4 text-gray-400">
                  <span>Semana {metricas?.semana_actual} de 48</span>
                  <span>•</span>
                  <span>Bloque {metricas?.bloque_actual}</span>
                </div>
              </div>

              {/* Main Metrics Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Overall Score Card */}
                <Card className="bg-[#1A2F47] border-[#2D3748] card-dark">
                  <CardHeader>
                    <CardTitle className="text-2xl font-bold text-white text-center">Puntuación Global</CardTitle>
                  </CardHeader>
                  <CardContent className="flex justify-center items-center py-8">
                    <CircularProgress 
                      percentage={Math.round((metricas?.comunicacion_efectiva + metricas?.feedback_constructivo + metricas?.gestion_conflictos + metricas?.delegacion + metricas?.inteligencia_emocional + metricas?.pensamiento_estrategico) / 6)} 
                      size={220}
                      strokeWidth={24}
                    />
                  </CardContent>
                </Card>

                {/* Performance by Module */}
                <Card className="bg-[#1A2F47] border-[#2D3748] card-dark">
                  <CardHeader>
                    <CardTitle className="text-2xl font-bold text-white">Competencias de Liderazgo</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4 py-4">
                    <HorizontalMetricBar label="Comunicación" value={metricas?.comunicacion_efectiva || 0} />
                    <HorizontalMetricBar label="Feedback" value={metricas?.feedback_constructivo || 0} />
                    <HorizontalMetricBar label="Gestión Conflictos" value={metricas?.gestion_conflictos || 0} />
                    <HorizontalMetricBar label="Inteligencia Emocional" value={metricas?.inteligencia_emocional || 0} />
                  </CardContent>
                </Card>
              </div>

              {/* Gamificación: Leaderboard y Badges */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Leaderboard */}
                <Card className="bg-[#1A2F47] border-[#2D3748] card-dark">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-white">
                      <Award className="w-5 h-5 text-yellow-500" />
                      <span>🏆 Tabla de Líderes</span>
                    </CardTitle>
                    <CardDescription className="text-gray-400">Top 10 participantes</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {leaderboard.length > 0 ? (
                      <div className="space-y-2">
                        {leaderboard.map((usuario, index) => (
                          <div 
                            key={index} 
                            className={`flex items-center justify-between p-3 rounded-lg ${
                              index === 0 ? 'bg-yellow-900/30 border border-yellow-600' :
                              index === 1 ? 'bg-gray-600/30 border border-gray-500' :
                              index === 2 ? 'bg-orange-900/30 border border-orange-600' :
                              'bg-slate-800/50'
                            }`}
                          >
                            <div className="flex items-center space-x-3">
                              <span className={`text-2xl font-bold ${
                                index === 0 ? 'text-yellow-400' :
                                index === 1 ? 'text-gray-300' :
                                index === 2 ? 'text-orange-400' :
                                'text-gray-500'
                              }`}>
                                {index + 1}°
                              </span>
                              <div>
                                <p className="text-white font-semibold">
                                  {usuario.nombre} {usuario.apellido}
                                  {usuario.user_id === user?.id && (
                                    <span className="ml-2 text-xs text-green-400">(Tú)</span>
                                  )}
                                </p>
                                <p className="text-gray-400 text-xs">{usuario.cargo || 'Participante'}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-green-400 font-bold text-lg">{usuario.puntos_totales} pts</div>
                              <div className="text-gray-400 text-xs">Nivel {usuario.nivel || 1}</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-400">
                        <Award className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>Sé el primero en el leaderboard</p>
                        <p className="text-sm mt-1">Participa y gana puntos</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Tus Stats y Badges */}
                <Card className="bg-[#1A2F47] border-[#2D3748] card-dark">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-white">
                      <Zap className="w-5 h-5 text-green-500" />
                      <span>Tus Estadísticas</span>
                    </CardTitle>
                    <CardDescription className="text-gray-400">Progreso y logros</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Stats del usuario */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-slate-800/50 p-4 rounded-lg text-center">
                          <div className="text-3xl font-bold text-green-400">
                            {user?.puntos_totales || 0}
                          </div>
                          <div className="text-gray-400 text-sm mt-1">Puntos Totales</div>
                        </div>
                        <div className="bg-slate-800/50 p-4 rounded-lg text-center">
                          <div className="text-3xl font-bold text-blue-400">
                            {metricas?.total_respuestas || 0}
                          </div>
                          <div className="text-gray-400 text-sm mt-1">Respuestas</div>
                        </div>
                        <div className="bg-slate-800/50 p-4 rounded-lg text-center">
                          <div className="text-3xl font-bold text-purple-400">
                            {userStats?.racha_dias || 0}
                          </div>
                          <div className="text-gray-400 text-sm mt-1">Racha (días)</div>
                        </div>
                        <div className="bg-slate-800/50 p-4 rounded-lg text-center">
                          <div className="text-3xl font-bold text-yellow-400">
                            {badges.length || 0}
                          </div>
                          <div className="text-gray-400 text-sm mt-1">Badges</div>
                        </div>
                      </div>

                      {/* Badges */}
                      {badges.length > 0 && (
                        <div className="mt-4">
                          <h4 className="text-white font-semibold mb-2">Tus Badges:</h4>
                          <div className="flex flex-wrap gap-2">
                            {badges.map((badge, idx) => (
                              <div 
                                key={idx}
                                className="bg-amber-900/30 border border-amber-600 px-3 py-1 rounded-full text-sm text-amber-300"
                                title={badge.descripcion}
                              >
                                {badge.icono} {badge.nombre}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Pregunta del Día */}
              {preguntaDia && !preguntaDia.respondida && preguntaDia.pregunta && (
                <Card className="bg-[#1A2F47] border-2 border-green-500 shadow-xl hover-lift" data-testid="pregunta-dia-card">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-white text-xl">🎯 Pregunta del Día</CardTitle>
                      <span className="text-xs bg-green-600 text-white px-3 py-1 rounded-full font-semibold">
                        {preguntaDia.tipo}
                      </span>
                    </div>
                    <CardDescription className="text-gray-400">Semana {preguntaDia.semana} • {preguntaDia.numero_envio}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-lg text-gray-200 leading-relaxed">{preguntaDia.pregunta}</p>
                    <div className="bg-green-900/30 border border-green-700 rounded-lg p-3">
                      <p className="text-sm text-green-300">
                        <strong>Competencia:</strong> {preguntaDia.competencia}
                      </p>
                    </div>
                    <div className="space-y-3">
                      <Textarea
                        placeholder="Escribe tu reflexión aquí..."
                        value={respuestaTexto}
                        onChange={(e) => setRespuestaTexto(e.target.value)}
                        rows={5}
                        className="resize-none bg-[#132337] border-gray-600 text-white placeholder:text-gray-500"
                        data-testid="textarea-respuesta"
                      />
                      <div className="flex items-center justify-between bg-slate-700 p-3 rounded-lg">
                        <span className="text-sm text-gray-300">O responde con audio:</span>
                        <Button
                          variant="outline"
                          size="sm"
                          className={grabando ? 
                            "border-red-500 text-red-400 hover:bg-red-500 hover:text-white animate-pulse" :
                            "border-green-500 text-green-400 hover:bg-green-500 hover:text-white"
                          }
                          onClick={handleToggleGrabacion}
                          disabled={loading}
                        >
                          {grabando ? (
                            <>
                              <MicOff className="w-4 h-4 mr-1" />
                              Detener
                            </>
                          ) : (
                            <>
                              <Mic className="w-4 h-4 mr-1" />
                              Grabar Audio
                            </>
                          )}
                        </Button>
                      </div>
                      {grabando && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mt-2 animate-pulse">
                          <p className="text-sm text-red-900 font-medium text-center">
                            🔴 Grabando... Habla ahora y luego haz clic en "Detener"
                          </p>
                        </div>
                      )}
                    </div>
                    <Button 
                      onClick={handleResponder}
                      disabled={loading}
                      className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold"
                      data-testid="btn-enviar-respuesta"
                    >
                      {loading ? 'Enviando...' : 'Enviar Respuesta'}
                      <Send className="w-4 h-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              )}

              {preguntaDia?.respondida && (
                <Card className="bg-green-900/20 border-2 border-green-600">
                  <CardContent className="py-6">
                    <div className="flex items-center space-x-3 text-green-400">
                      <CheckCircle className="w-6 h-6" />
                      <span className="font-semibold">¡Ya respondiste la pregunta de hoy! Regresa el próximo día L-M-V.</span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {preguntaDia?.mensaje && !preguntaDia.pregunta && (
                <Card className="bg-[#1A2F47] border-[#2D3748]">
                  <CardContent className="py-6">
                    <div className="flex items-center space-x-3 text-gray-400">
                      <Clock className="w-6 h-6" />
                      <span>{preguntaDia.mensaje}</span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Additional Metrics Cards */}
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="bg-[#1A2F47] border-[#2D3748] metric-card hover-lift">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <Award className="w-8 h-8 text-green-400" />
                      <span className="text-3xl font-bold text-white">{metricas?.total_respuestas || 0}</span>
                    </div>
                    <p className="text-sm text-gray-400">Respuestas Completadas</p>
                  </CardContent>
                </Card>

                <Card className="bg-[#1A2F47] border-[#2D3748] metric-card hover-lift">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <Target className="w-8 h-8 text-green-400" />
                      <span className="text-3xl font-bold text-white">{metricas?.progreso_programa}%</span>
                    </div>
                    <p className="text-sm text-gray-400">Progreso Programa</p>
                  </CardContent>
                </Card>

                <Card className="bg-[#1A2F47] border-[#2D3748] metric-card hover-lift">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <Zap className="w-8 h-8 text-green-400" />
                      <span className="text-3xl font-bold text-white">7</span>
                    </div>
                    <p className="text-sm text-gray-400">Racha de Días</p>
                  </CardContent>
                </Card>

                <Card className="bg-[#1A2F47] border-[#2D3748] metric-card hover-lift">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <TrendingUp className="w-8 h-8 text-green-400" />
                      <span className="text-3xl font-bold text-white">+12%</span>
                    </div>
                    <p className="text-sm text-gray-400">Mejora Mes Actual</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="lmv" className="mt-6">
            <div className="space-y-6">
              <Card className="bg-[#1A2F47] border-[#2D3748]">
                <CardHeader>
                  <CardTitle className="text-white text-2xl">Mis Respuestas L-M-V</CardTitle>
                  <CardDescription className="text-gray-400">Historial de tus reflexiones semanales</CardDescription>
                </CardHeader>
                <CardContent>
                  {misRespuestas.length === 0 ? (
                    <p className="text-gray-400 text-center py-8">Aún no has recibido ninguna pregunta</p>
                  ) : (
                    <div className="space-y-4">
                      {misRespuestas.map((respuesta, index) => (
                        <Card key={index} className={`${respuesta.respuesta ? 'bg-[#132337]' : 'bg-gradient-to-r from-blue-900/30 to-amber-900/30 border-blue-500'} border-gray-700 hover-lift`}>
                          <CardHeader>
                            <div className="flex justify-between items-start">
                              <div>
                                <CardTitle className="text-sm text-white flex items-center gap-2">
                                  Semana {respuesta.semana} • {respuesta.numero_envio}
                                  {!respuesta.respuesta && (
                                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded-full">Pendiente</span>
                                  )}
                                </CardTitle>
                                <p className="text-xs text-gray-400 mt-1">{respuesta.tipo} • {respuesta.competencia}</p>
                              </div>
                              <span className="text-xs text-gray-500">
                                {respuesta.fecha_respuesta 
                                  ? new Date(respuesta.fecha_respuesta).toLocaleDateString('es-ES')
                                  : 'Sin responder'
                                }
                              </span>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <CardDescription className="text-sm text-gray-300 mb-3 font-medium">
                              📝 {respuesta.pregunta}
                            </CardDescription>
                            {respuesta.respuesta ? (
                              <div className="mt-3 p-3 bg-[#0A1628] rounded-lg">
                                <p className="text-sm text-gray-300">{respuesta.respuesta}</p>
                                {respuesta.puntos_otorgados > 0 && (
                                  <p className="text-xs text-amber-500 mt-2">+{respuesta.puntos_otorgados} puntos</p>
                                )}
                              </div>
                            ) : (
                              <div className="mt-3 p-4 bg-blue-900/20 rounded-lg border border-blue-700">
                                <p className="text-sm text-blue-300 mb-3">
                                  💡 Esta pregunta está esperando tu respuesta. Reflexiona y comparte tu perspectiva.
                                </p>
                                <Button 
                                  className="bg-blue-600 hover:bg-blue-700 text-white"
                                  size="sm"
                                  disabled
                                >
                                  Responder (Próximamente)
                                </Button>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DashboardPage;
