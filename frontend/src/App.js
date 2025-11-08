import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

import LoginPasswordless from './components/LoginPasswordless';
import EnrollPasskey from './components/EnrollPasskey';
import Dashboard from './components/Dashboard';
import LandingPage from './components/LandingPage';
import AdminPanel from './components/AdminPanel';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData, tokens) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Cargando...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>🔐 Prototipo Autenticación Passkeys + Zero Trust</h1>
          <p className="subtitle">TFG - Universidad Siglo 21 | Zuy, Ariel Hernán</p>
        </header>

        <Routes>
          <Route 
            path="/" 
            element={
              user ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LandingPage />
              )
            } 
          />

          <Route 
            path="/login" 
            element={
              user ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <LoginPasswordless onLogin={handleLogin} />
              )
            } 
          />

          <Route 
            path="/enroll" 
            element={
              user ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <EnrollPasskey />
              )
            } 
          />

          <Route 
            path="/dashboard" 
            element={
              user ? (
                <Dashboard user={user} onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />

          <Route 
            path="/admin" 
            element={
              user ? (
                <AdminPanel onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
