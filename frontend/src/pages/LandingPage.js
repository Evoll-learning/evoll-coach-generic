import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Brain, Users, Target, TrendingUp, MessageSquare, Award, CheckCircle, ArrowRight, Sparkles, Heart, Clock, Shield } from 'lucide-react';
import { toast } from 'sonner';

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, login, register } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nombre: '',
    apellido: ''
  });

  React.useEffect(() => {
    if (user) {
      if (!user.onboarding_completado) {
        navigate('/onboarding');
      } else {
        navigate('/dashboard');
      }
    }
  }, [user, navigate]);

  const handleAuth = async (e) => {
    e.preventDefault();
    try {
      if (authMode === 'login') {
        await login(formData.email, formData.password);
        toast.success('¡Bienvenido de vuelta!');
      } else {
        await register(formData.email, formData.password, formData.nombre, formData.apellido);
        toast.success('¡Cuenta creada exitosamente!');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Error en autenticación');
    }
  };

  const modulos = [
    {
      numero: 1,
      titulo: 'Autoconocimiento y Autenticidad',
      duracion: '2 meses',
      temas: ['Evaluación 360°', 'Perfil de energías cromáticas', 'Estilo personal de liderazgo', 'Valores y propósito']
    },
    {
      numero: 2,
      titulo: 'Coaching Personal',
      duracion: '2 meses',
      temas: ['Sesiones personalizadas', 'Brecha intención-impacto', 'Plan de transformación', 'Nuevos hábitos']
    },
    {
      numero: 3,
      titulo: 'Liderazgo Relacional',
      duracion: '3 meses',
      temas: ['Comunicación efectiva', 'Feedback constructivo', 'Influencia y negociación', 'Gestión de conflictos']
    },
    {
      numero: 4,
      titulo: 'Liderazgo Estratégico',
      duracion: '3 meses',
      temas: ['Modelos organizacionales', 'Inteligencia emocional', 'Cultura empresarial', 'Decisiones basadas en datos']
    },
    {
      numero: 5,
      titulo: 'Transformación Final',
      duracion: '2 meses',
      temas: ['Workshop de cierre', 'Compromisos de cambio', 'Validación de resultados', 'Plan post-programa']
    }
  ];

  const valoresOrenes = [
    { icon: Clock, titulo: 'Experiencia', descripcion: '56 años liderando el sector del ocio y entretenimiento en España' },
    { icon: Shield, titulo: 'Confianza', descripcion: 'Transparencia y relaciones sólidas con todos nuestros grupos de interés' },
    { icon: Heart, titulo: 'Compromiso', descripcion: 'Sentimiento familiar, generosidad y humildad en cada acción' },
    { icon: Users, titulo: 'Comunidad', descripcion: '+3,000 profesionales comprometidos con la excelencia' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-green-900">
      {/* Header */}
      <header className="fixed top-0 w-full bg-slate-900/95 backdrop-blur-md border-b border-green-500/20 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-600 to-green-400 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/30">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">EvoLL</h1>
              <p className="text-xs text-green-400 font-medium">Grupo Orenes</p>
            </div>
          </div>
          <Button 
            onClick={() => setShowAuth(true)}
            className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold px-6 shadow-lg shadow-green-500/30"
            data-testid="login-button"
          >
            Acceder
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center animate-fade-in">
            <h2 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              Tu viaje de
              <span className="gradient-text-green"> transformación</span>
              <br />como líder comienza aquí
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
              Programa de Liderazgo Evolutivo de 12 meses con IA Conversacional.
              Desarrolla tu máximo potencial con acompañamiento inteligente y personalizado.
            </p>
            <Button 
              size="lg" 
              onClick={() => setShowAuth(true)}
              className="bg-gradient-to-r from-green-700 to-green-500 hover:from-green-800 hover:to-green-600 text-white text-lg px-8 py-6 rounded-full shadow-xl hover-lift"
              data-testid="cta-comenzar"
            >
              Comenzar mi transformación
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </section>

      {/* Cómo Funciona */}
      <section className="py-20 bg-slate-900">
        <div className="container mx-auto px-6 max-w-6xl">
          <h3 className="text-4xl font-bold text-center mb-4 text-white">
            ¿Cómo funciona el programa?
          </h3>
          <p className="text-center text-gray-400 mb-16 text-lg">Sistema L-M-V: Lunes, Miércoles y Viernes</p>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { icon: Brain, titulo: 'Micro-learnings', desc: 'Preguntas reflexivas 3 veces por semana' },
              { icon: MessageSquare, titulo: 'Responder', desc: 'Comparte tus reflexiones por texto o audio' },
              { icon: Sparkles, titulo: 'Coach IA', desc: 'Feedback personalizado instantáneo' },
              { icon: TrendingUp, titulo: 'Evaluación', desc: 'Métricas mensuales de tu progreso' }
            ].map((paso, index) => (
              <Card key={index} className="hover-lift bg-slate-800 border-2 border-green-500/30 hover:border-green-500 transition-all group">
                <CardHeader>
                  <div className="w-16 h-16 bg-gradient-to-br from-green-600 to-green-400 rounded-2xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-green-500/30 group-hover:scale-110 transition-transform">
                    <paso.icon className="w-8 h-8 text-white" />
                  </div>
                  <CardTitle className="text-center text-white font-bold">{paso.titulo}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-center text-gray-300 text-sm">{paso.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Módulos del Programa */}
      <section className="py-20 bg-slate-800">
        <div className="container mx-auto px-6 max-w-6xl">
          <h3 className="text-4xl font-bold text-center mb-4 text-white">Programa Completo</h3>
          <p className="text-center text-gray-400 mb-12 text-lg">5 módulos diseñados para tu evolución progresiva durante 12 meses</p>
          <div className="space-y-6">
            {modulos.map((modulo) => (
              <Card key={modulo.numero} className="hover-lift bg-slate-900 border-2 border-green-500/30 hover:border-green-500 transition-all">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-14 h-14 bg-gradient-to-br from-green-600 to-green-400 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/30">
                        <span className="text-white font-bold text-2xl">{modulo.numero}</span>
                      </div>
                      <div>
                        <CardTitle className="text-white text-lg">{modulo.titulo}</CardTitle>
                        <CardDescription className="text-green-400 font-medium">{modulo.duracion}</CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {modulo.temas.map((tema, idx) => (
                      <div key={idx} className="flex items-center space-x-2 text-gray-300">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <span className="text-sm">{tema}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Valores Orenes */}
      <section className="py-20 bg-gradient-to-br from-green-900 via-green-800 to-slate-900 text-white">
        <div className="container mx-auto px-6 max-w-6xl">
          <h3 className="text-4xl font-bold text-center mb-4">Únete a nuestro equipo</h3>
          <p className="text-center text-green-200 mb-12 text-lg">Grupo Orenes - Líderes en ocio y entretenimiento</p>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {valoresOrenes.map((valor, index) => (
              <Card key={index} className="bg-white/10 border-green-500/30 backdrop-blur-sm hover-lift hover:border-green-400 transition-all">
                <CardHeader>
                  <valor.icon className="w-12 h-12 text-green-400 mb-3" />
                  <CardTitle className="text-white">{valor.titulo}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-200">{valor.descripcion}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Beneficios */}
      <section className="py-20 bg-slate-900">
        <div className="container mx-auto px-6 max-w-6xl">
          <h3 className="text-4xl font-bold text-center mb-4 text-white">Beneficios del Programa</h3>
          <p className="text-center text-gray-400 mb-16 text-lg">Impacto transformador a todos los niveles</p>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { 
                icon: Target, 
                titulo: 'Individual', 
                items: ['Crecimiento continuo', 'Feedback objetivo', 'Autoliderazgo', 'Mayor compromiso'] 
              },
              { 
                icon: Users, 
                titulo: 'Equipo', 
                items: ['Mejor comunicación', 'Equipos cohesionados', 'Motivación alta', 'Clima positivo'] 
              },
              { 
                icon: Award, 
                titulo: 'Organizacional', 
                items: ['Cultura coherente', 'Decisión basada en datos', 'Estandarización', 'Retención talento'] 
              }
            ].map((beneficio, index) => (
              <Card key={index} className="hover-lift bg-slate-800 border-2 border-green-500/30 hover:border-green-500 transition-all">
                <CardHeader>
                  <beneficio.icon className="w-12 h-12 text-green-400 mb-4" />
                  <CardTitle className="text-white text-xl">{beneficio.titulo}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {beneficio.items.map((item, idx) => (
                      <li key={idx} className="flex items-center space-x-2 text-gray-300">
                        <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-gradient-to-r from-green-700 via-green-600 to-green-500">
        <div className="container mx-auto px-6 text-center">
          <h3 className="text-4xl font-bold text-white mb-6">Comienza tu transformación hoy</h3>
          <p className="text-xl text-white/95 mb-8 max-w-2xl mx-auto">
            Únete a los líderes de Orenes que están desarrollando su máximo potencial
          </p>
          <Button 
            size="lg" 
            onClick={() => setShowAuth(true)}
            className="bg-white text-green-700 hover:bg-slate-100 text-lg px-8 py-6 rounded-full shadow-xl hover-lift font-semibold"
            data-testid="cta-final"
          >
            Empezar ahora
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </div>
      </section>

      {/* Auth Dialog */}
      <Dialog open={showAuth} onOpenChange={setShowAuth}>
        <DialogContent className="sm:max-w-md" data-testid="auth-dialog">
          <DialogHeader>
            <DialogTitle>Accede a EvoLL</DialogTitle>
            <DialogDescription>
              Comienza tu programa de liderazgo personalizado
            </DialogDescription>
          </DialogHeader>
          <Tabs value={authMode} onValueChange={setAuthMode}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login" data-testid="tab-login">Iniciar Sesión</TabsTrigger>
              <TabsTrigger value="register" data-testid="tab-register">Registrarse</TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <form onSubmit={handleAuth} className="space-y-4">
                <Input
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  data-testid="input-email"
                />
                <Input
                  type="password"
                  placeholder="Contraseña"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  data-testid="input-password"
                />
                <Button type="submit" className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold" data-testid="btn-login-submit">
                  Iniciar Sesión
                </Button>
              </form>
            </TabsContent>
            <TabsContent value="register">
              <form onSubmit={handleAuth} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    placeholder="Nombre"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    required
                    data-testid="input-nombre"
                  />
                  <Input
                    placeholder="Apellido"
                    value={formData.apellido}
                    onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                    required
                    data-testid="input-apellido"
                  />
                </div>
                <Input
                  type="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  data-testid="input-email-register"
                />
                <Input
                  type="password"
                  placeholder="Contraseña"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  data-testid="input-password-register"
                />
                <Button type="submit" className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold" data-testid="btn-register-submit">
                  Crear Cuenta
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LandingPage;