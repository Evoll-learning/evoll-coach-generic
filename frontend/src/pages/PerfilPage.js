import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, User, Mail, Briefcase, Users as UsersIcon, Target, Calendar, MessageSquare, FileText, Download, Video, Book, CheckCircle, XCircle } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PerfilPage = () => {
  const navigate = useNavigate();
  const { user, setUser } = useAuth();
  const [codigoTelegram, setCodigoTelegram] = useState('');
  const [loadingVinculacion, setLoadingVinculacion] = useState(false);
  const [loadingTest, setLoadingTest] = useState(false);

  const handleVincularTelegram = async () => {
    if (!codigoTelegram.trim()) {
      toast.error('Por favor ingresa el código de vinculación');
      return;
    }

    setLoadingVinculacion(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/telegram/vincular`,
        { codigo_vinculacion: codigoTelegram },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('¡Telegram vinculado exitosamente! 🎉');
      
      // Actualizar user context
      const updatedUser = { ...user, telegram_chat_id: response.data.chat_id };
      setUser(updatedUser);
      setCodigoTelegram('');
    } catch (error) {
      console.error('Error vinculando Telegram:', error);
      toast.error(error.response?.data?.detail || 'Error al vincular Telegram');
    } finally {
      setLoadingVinculacion(false);
    }
  };

  const handleEnviarPrueba = async () => {
    setLoadingTest(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/telegram/test`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Notificación de prueba enviada. Revisa tu Telegram!');
    } catch (error) {
      console.error('Error enviando prueba:', error);
      toast.error(error.response?.data?.detail || 'Error al enviar notificación');
    } finally {
      setLoadingTest(false);
    }
  };

  const handleDesvincular = async () => {
    if (!confirm('¿Estás seguro de que deseas desvincular tu Telegram? Dejarás de recibir notificaciones.')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `${API_URL}/telegram/desvincular`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Telegram desvinculado');
      
      // Actualizar user context
      const updatedUser = { ...user, telegram_chat_id: null };
      setUser(updatedUser);
    } catch (error) {
      console.error('Error desvinculando:', error);
      toast.error('Error al desvincular Telegram');
    }
  };

  const infoSections = [
    {
      icon: User,
      titulo: 'Información Personal',
      datos: [
        { label: 'Nombre', value: `${user?.nombre} ${user?.apellido}` },
        { label: 'Email', value: user?.email }
      ]
    },
    {
      icon: Briefcase,
      titulo: 'Información Profesional',
      datos: [
        { label: 'Cargo', value: user?.cargo || 'No especificado' },
        { label: 'División', value: user?.division || 'No especificado' },
        { label: 'Años de experiencia', value: user?.experiencia_anos ? `${user.experiencia_anos} años` : 'No especificado' }
      ]
    },
    {
      icon: UsersIcon,
      titulo: 'Tu Equipo',
      datos: [
        { label: 'Tamaño del equipo', value: user?.tamano_equipo ? `${user.tamano_equipo} personas` : 'No especificado' },
        { label: 'Desafíos principales', value: user?.desafios_equipo || 'No especificado' }
      ]
    },
    {
      icon: Target,
      titulo: 'Objetivos y Compromisos',
      datos: [
        { label: 'Objetivos personales', value: user?.objetivos_personales || 'No especificado' },
        { label: 'Compromiso con valores', value: user?.valores_compromiso || 'No especificado' }
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-[#0A1628]">
      {/* Header */}
      <header className="bg-[#132337] border-b border-[#2D3748] sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} data-testid="btn-back">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-xl font-bold text-white">Mi Perfil</h1>
              <p className="text-sm text-gray-400">Información personal y profesional</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Profile Header */}
        <Card className="mb-8 bg-gradient-to-r from-green-700 to-green-500 text-white border-0 shadow-xl">
          <CardContent className="py-8">
            <div className="flex items-center space-x-6">
              <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center text-4xl font-bold backdrop-blur-sm">
                {user?.nombre?.[0]}{user?.apellido?.[0]}
              </div>
              <div>
                <h2 className="text-3xl font-bold mb-2">{user?.nombre} {user?.apellido}</h2>
                <p className="text-blue-100 flex items-center space-x-2">
                  <Mail className="w-4 h-4" />
                  <span>{user?.email}</span>
                </p>
                <p className="text-blue-100 flex items-center space-x-2 mt-1">
                  <Calendar className="w-4 h-4" />
                  <span>Miembro desde {new Date(user?.fecha_registro).toLocaleDateString('es-ES')}</span>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Configuración de Notificaciones */}
        <Card className="mb-6 bg-[#1A2F47] border-[#2D3748]">
          <CardHeader>
            <CardTitle className="text-white flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <MessageSquare className="w-6 h-6 text-green-400" />
                <span>Notificaciones de Telegram</span>
              </div>
              {user?.telegram_chat_id && (
                <span className="flex items-center space-x-1 text-sm text-green-400">
                  <CheckCircle className="w-4 h-4" />
                  <span>Vinculado</span>
                </span>
              )}
            </CardTitle>
            <CardDescription className="text-gray-400">
              Recibe tus preguntas L-M-V semanales directamente en Telegram
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!user?.telegram_chat_id ? (
              <div className="bg-slate-800 p-5 rounded-lg space-y-4">
                <div className="space-y-2">
                  <p className="text-green-400 font-semibold">📱 Cómo vincular tu Telegram:</p>
                  <ol className="text-gray-300 text-sm space-y-2 ml-4">
                    <li>1. Abre Telegram y busca: <code className="bg-slate-700 px-2 py-1 rounded text-green-400 font-mono">@EvoLL_Coach_Bot</code></li>
                    <li>2. Inicia conversación enviando: <code className="bg-slate-700 px-2 py-1 rounded text-green-400 font-mono">/start</code></li>
                    <li>3. El bot te dará un código como: <code className="bg-slate-700 px-2 py-1 rounded text-yellow-400 font-mono">EVOLL-123456789</code></li>
                    <li>4. Copia ese código y pégalo aquí abajo:</li>
                  </ol>
                </div>
                
                <div className="flex gap-2">
                  <Input 
                    placeholder="EVOLL-123456789"
                    value={codigoTelegram}
                    onChange={(e) => setCodigoTelegram(e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white font-mono"
                    disabled={loadingVinculacion}
                  />
                  <Button 
                    onClick={handleVincularTelegram}
                    disabled={loadingVinculacion || !codigoTelegram.trim()}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    {loadingVinculacion ? 'Vinculando...' : 'Vincular'}
                  </Button>
                </div>
                
                <div className="bg-blue-900/30 border border-blue-700 rounded p-3">
                  <p className="text-blue-300 text-xs">
                    💡 <strong>Privacidad:</strong> Solo tú recibirás notificaciones. Tus respuestas son completamente privadas.
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-slate-800 p-5 rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-green-400 font-semibold flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5" />
                      <span>¡Telegram vinculado!</span>
                    </p>
                    <p className="text-gray-400 text-sm mt-1">
                      Recibirás notificaciones cada Lunes, Miércoles y Viernes
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button 
                    onClick={handleEnviarPrueba}
                    disabled={loadingTest}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    {loadingTest ? 'Enviando...' : '📤 Enviar Prueba'}
                  </Button>
                  <Button 
                    onClick={handleDesvincular}
                    variant="outline"
                    className="border-red-600 text-red-400 hover:bg-red-900/20"
                  >
                    🔗 Desvincular
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* WhatsApp - Coming Soon */}
        <Card className="mb-6 bg-[#1A2F47] border-[#2D3748]">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <MessageSquare className="w-6 h-6 text-gray-400" />
              <span className="text-gray-400">Notificaciones de WhatsApp</span>
              <span className="text-xs bg-yellow-600 text-white px-2 py-1 rounded">Próximamente</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-400 text-sm">
              Pronto podrás recibir notificaciones también por WhatsApp
            </p>
          </CardContent>
        </Card>

        {/* Recursos del Módulo */}
        <Card className="mb-6 bg-[#1A2F47] border-[#2D3748]">
          <CardHeader>
            <CardTitle className="text-white flex items-center space-x-2">
              <Briefcase className="w-6 h-6 text-green-400" />
              <span>Recursos del Módulo Actual</span>
            </CardTitle>
            <CardDescription className="text-gray-400">
              Bloque {user?.bloque_actual} - Semana {user?.semana_actual}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="bg-slate-800 p-3 rounded-lg hover:bg-slate-700 cursor-pointer transition">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Guía del módulo</p>
                      <p className="text-sm text-gray-400">PDF - 2.5 MB</p>
                    </div>
                  </div>
                  <Download className="w-5 h-5 text-gray-400" />
                </div>
              </div>
              
              <div className="bg-slate-800 p-3 rounded-lg hover:bg-slate-700 cursor-pointer transition">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                      <Video className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Vídeo explicativo</p>
                      <p className="text-sm text-gray-400">MP4 - 15 min</p>
                    </div>
                  </div>
                  <Download className="w-5 h-5 text-gray-400" />
                </div>
              </div>
              
              <div className="bg-slate-800 p-3 rounded-lg hover:bg-slate-700 cursor-pointer transition">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                      <Book className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Ejercicios prácticos</p>
                      <p className="text-sm text-gray-400">PDF - 1.8 MB</p>
                    </div>
                  </div>
                  <Download className="w-5 h-5 text-gray-400" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Info Sections */}
        <div className="space-y-6">
          {infoSections.map((section, index) => (
            <Card key={index} className="bg-[#1A2F47] border-[#2D3748] hover-lift" data-testid={`section-${index}`}>
              <CardHeader>
                <CardTitle className="flex items-center space-x-3 text-white">
                  <section.icon className="w-6 h-6 text-green-400" />
                  <span>{section.titulo}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {section.datos.map((dato, idx) => (
                    <div key={idx} className="border-b border-[#2D3748] pb-3 last:border-0 last:pb-0">
                      <p className="text-sm font-medium text-gray-400 mb-1">{dato.label}</p>
                      <p className="text-white">{dato.value}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PerfilPage;