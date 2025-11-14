import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

const API_URL = `https://evoll-coach-generic-production.up.railway.app/api`;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API_URL}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Error fetching user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      console.log('🔐 Intentando login con:', email);
      console.log('📡 API URL:', API_URL);
      const response = await axios.post(`${API_URL}/auth/login`, { email, password });
      console.log('✅ Login exitoso:', response.data);
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      return userData;
    } catch (error) {
      console.error('❌ Error en login:', error.response?.data || error.message);
      throw error;
    }
  };

  const register = async (email, password, nombre, apellido) => {
    try {
      console.log('📝 Intentando registro con:', email);
      console.log('📡 API URL:', API_URL);
      const response = await axios.post(`${API_URL}/auth/register`, {
        email,
        password,
        nombre,
        apellido
      });
      console.log('✅ Registro exitoso:', response.data);
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      return userData;
    } catch (error) {
      console.error('❌ Error en registro:', error.response?.data || error.message);
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const completeOnboarding = async (data) => {
    await axios.put(`${API_URL}/auth/onboarding`, data);
    await fetchUser();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, completeOnboarding, token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};