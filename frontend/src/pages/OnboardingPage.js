import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CheckCircle, ArrowRight, ArrowLeft, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const OnboardingPage = () => {
  const navigate = useNavigate();
  const { user, completeOnboarding } = useAuth();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    cargo: '',
    division: '',
    experiencia_anos: '',
    tamano_equipo: '',
    desafios_equipo: '',
    objetivos_personales: '',
    valores_compromiso: ''
  });

  const totalSteps = 6;
  const progress = (step / totalSteps) * 100;

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      await completeOnboarding({
        cargo: formData.cargo,
        division: formData.division,
        experiencia_anos: parseInt(formData.experiencia_anos),
        tamano_equipo: parseInt(formData.tamano_equipo),
        desafios_equipo: formData.desafios_equipo,
        objetivos_personales: formData.objetivos_personales,
        valores_compromiso: formData.valores_compromiso
      });
      toast.success('¡Onboarding completado!');
      navigate('/dashboard');
    } catch (error) {
      toast.error('Error al completar onboarding');
    }
  };

  const renderStep = () => {
    switch(step) {
      case 1:
        return (
          <div className="space-y-6 animate-fade-in">
            <div className="text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-900 to-amber-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Sparkles className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-slate-900 mb-4">¡Bienvenido/a, {user?.nombre}!</h2>
              <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                Estás a punto de comenzar un viaje transformador de 12 meses. En los próximos pasos, 
                personalizaremos tu experiencia para maximizar tu desarrollo como líder.
              </p>
            </div>
            <Card className="border-2 border-blue-100 bg-blue-50/50">
              <CardHeader>
                <CardTitle className="text-blue-900">Qué esperar del programa</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  'Micro-reflexiones 3 veces por semana (Lunes, Miércoles, Viernes)',
                  'Feedback personalizado de tu Coach IA',
                  'Evaluaciones mensuales de progreso',
                  'Acceso a comunidad de líderes',
                  'Métricas en tiempo real de tu desarrollo'
                ].map((item, idx) => (
                  <div key={idx} className="flex items-center space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                    <span className="text-slate-700">{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        );
      
      case 2:
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">Información Personal</h2>
              <p className="text-slate-600">Comencemos conociendo tu contexto profesional</p>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Email</label>
                <Input value={user?.email} disabled className="bg-slate-200 text-slate-600" data-testid="input-email" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Nombre</label>
                  <Input value={user?.nombre} disabled className="bg-slate-200 text-slate-600" data-testid="input-nombre" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Apellido</label>
                  <Input value={user?.apellido} disabled className="bg-slate-200 text-slate-600" data-testid="input-apellido" />
                </div>
              </div>
            </div>
          </div>
        );
      
      case 3:
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">Tu Rol en Orenes</h2>
              <p className="text-slate-600">Ayuda a personalizar tu experiencia de aprendizaje</p>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-white mb-2">Cargo Actual</label>
                <Input 
                  placeholder="Ej: Gerente de Operaciones"
                  value={formData.cargo}
                  onChange={(e) => setFormData({...formData, cargo: e.target.value})}
                  data-testid="input-cargo"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-white mb-2">División / Área</label>
                <Select value={formData.division} onValueChange={(value) => setFormData({...formData, division: value})}>
                  <SelectTrigger className="bg-white border-slate-600 text-slate-900" data-testid="select-division">
                    <SelectValue placeholder="Selecciona tu división" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="operaciones">Operaciones</SelectItem>
                    <SelectItem value="ventas">Ventas</SelectItem>
                    <SelectItem value="rrhh">Recursos Humanos</SelectItem>
                    <SelectItem value="atencion-cliente">Atención al Cliente</SelectItem>
                    <SelectItem value="finanzas">Finanzas</SelectItem>
                    <SelectItem value="direccion">Dirección</SelectItem>
                    <SelectItem value="otro">Otro</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-white mb-2">Años de experiencia en liderazgo</label>
                <Input 
                  type="number"
                  placeholder="Ej: 5"
                  value={formData.experiencia_anos}
                  onChange={(e) => setFormData({...formData, experiencia_anos: e.target.value})}
                  data-testid="input-experiencia"
                />
              </div>
            </div>
          </div>
        );
      
      case 4:
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">Tu Equipo</h2>
              <p className="text-slate-600">Conocer tu contexto de liderazgo nos ayuda a personalizar el contenido</p>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-white mb-2">Tamaño de tu equipo</label>
                <Input 
                  type="number"
                  placeholder="Número de personas que lideras directamente"
                  value={formData.tamano_equipo}
                  onChange={(e) => setFormData({...formData, tamano_equipo: e.target.value})}
                  data-testid="input-tamano-equipo"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-white mb-2">
                  ¿Cuáles son los principales desafíos de tu equipo?
                </label>
                <Textarea 
                  placeholder="Describe los retos más importantes que enfrenta tu equipo actualmente..."
                  value={formData.desafios_equipo}
                  onChange={(e) => setFormData({...formData, desafios_equipo: e.target.value})}
                  rows={4}
                  data-testid="textarea-desafios"
                />
              </div>
            </div>
          </div>
        );
      
      case 5:
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">Tus Objetivos</h2>
              <p className="text-slate-600">Define qué quieres lograr en estos 12 meses</p>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-white mb-2">
                  ¿Qué esperas conseguir con este programa?
                </label>
                <Textarea 
                  placeholder="Describe tus metas personales y profesionales para el programa..."
                  value={formData.objetivos_personales}
                  onChange={(e) => setFormData({...formData, objetivos_personales: e.target.value})}
                  rows={5}
                  data-testid="textarea-objetivos"
                />
                <p className="text-sm text-gray-400 mt-2">
                  Ejemplos: Mejorar mi comunicación con el equipo, desarrollar mayor confianza en la toma de decisiones, 
                  gestionar mejor el estrés, etc.
                </p>
              </div>
            </div>
          </div>
        );
      
      case 6:
        return (
          <div className="space-y-6 animate-fade-in">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-2">Compromiso con Valores</h2>
              <p className="text-slate-600">Alineación con los valores de Orenes</p>
            </div>
            <Card className="border-2 border-blue-100 bg-blue-50/50 mb-6">
              <CardHeader>
                <CardTitle className="text-blue-900">Valores Orenes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { titulo: 'Experiencia', desc: '56 años de trayectoria' },
                    { titulo: 'Confianza', desc: 'Transparencia en todo' },
                    { titulo: 'Compromiso', desc: 'Con personas y sociedad' },
                    { titulo: 'Familia', desc: 'Sentimiento de pertenencia' }
                  ].map((valor, idx) => (
                    <div key={idx} className="flex items-start space-x-2">
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-slate-900">{valor.titulo}</p>
                        <p className="text-sm text-slate-600">{valor.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <div>
              <label className="block text-sm font-semibold text-white mb-2">
                ¿Cómo te comprometes a vivir estos valores en tu liderazgo?
              </label>
              <Textarea 
                placeholder="Describe tu compromiso personal con los valores de Orenes..."
                value={formData.valores_compromiso}
                onChange={(e) => setFormData({...formData, valores_compromiso: e.target.value})}
                rows={5}
                data-testid="textarea-valores"
              />
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-green-900 py-12 px-6">
      <div className="container mx-auto max-w-3xl">
        {/* Progress Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold text-white">Configuración Inicial</h1>
            <span className="text-sm text-gray-400">Paso {step} de {totalSteps}</span>
          </div>
          <Progress value={progress} className="h-2" data-testid="progress-bar" />
        </div>

        {/* Content Card */}
        <Card className="shadow-xl bg-slate-800 border-2 border-slate-700">
          <CardContent className="pt-8 pb-8">
            {renderStep()}
          </CardContent>
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={step === 1}
            data-testid="btn-back"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Atrás
          </Button>
          
          {step < totalSteps ? (
            <Button
              onClick={handleNext}
              className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold"
              data-testid="btn-next"
            >
              Siguiente
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-semibold"
              data-testid="btn-finish"
            >
              Completar
              <CheckCircle className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;