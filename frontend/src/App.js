import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import LandingPage from '@/pages/LandingPage';
import OnboardingPage from '@/pages/OnboardingPage';
import DashboardPage from '@/pages/DashboardPage';
import ComunidadPage from '@/pages/ComunidadPage';
import CoachIAPage from '@/pages/CoachIAPage';
import PerfilPage from '@/pages/PerfilPage';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>;
  }
  
  return user ? children : <Navigate to="/" replace />;
};

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/onboarding" element={
        <PrivateRoute>
          <OnboardingPage />
        </PrivateRoute>
      } />
      <Route path="/dashboard" element={
        <PrivateRoute>
          <DashboardPage />
        </PrivateRoute>
      } />
      <Route path="/comunidad" element={
        <PrivateRoute>
          <ComunidadPage />
        </PrivateRoute>
      } />
      <Route path="/coach" element={
        <PrivateRoute>
          <CoachIAPage />
        </PrivateRoute>
      } />
      <Route path="/perfil" element={
        <PrivateRoute>
          <PerfilPage />
        </PrivateRoute>
      } />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
        <Toaster position="top-center" />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;