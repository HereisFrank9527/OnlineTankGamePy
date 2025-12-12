import React, { useEffect } from 'react';
import { useAuthStore, useUIStore } from './store';
import LoginView from './views/LoginView';
import LobbyView from './views/LobbyView';
import GameView from './views/GameView';
import './App.css';

const App: React.FC = () => {
  const { isAuthenticated, user, login } = useAuthStore();
  const { currentView, error, hideError } = useUIStore();

  useEffect(() => {
    // Check for stored tokens on app load
    const tokens = localStorage.getItem('tokens');
    if (tokens && isAuthenticated) {
      try {
        const parsedTokens = JSON.parse(tokens);
        // In a real app, you'd validate the token with the backend
        // For now, we'll just check if it exists
        useUIStore.getState().setCurrentView('lobby');
      } catch (error) {
        console.error('Invalid stored tokens:', error);
        localStorage.removeItem('tokens');
      }
    }
  }, [isAuthenticated]);

  useEffect(() => {
    // Auto-hide errors after 5 seconds
    if (error) {
      const timer = setTimeout(() => {
        hideError();
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, hideError]);

  const renderCurrentView = () => {
    switch (currentView) {
      case 'login':
        return <LoginView />;
      case 'lobby':
        return <LobbyView />;
      case 'game':
        return <GameView />;
      default:
        return <LoginView />;
    }
  };

  return (
    <div className="app">
      {error && (
        <div className="error-banner">
          {error}
          <button onClick={hideError} className="error-close">
            ×
          </button>
        </div>
      )}
      
      <div className="app-header">
        <h1>Tank Game</h1>
        {user && (
          <div className="user-info">
            <span>Welcome, {user.username}</span>
            <button 
              onClick={() => {
                useAuthStore.getState().logout();
                useUIStore.getState().setCurrentView('login');
              }}
              className="logout-btn"
            >
              Logout
            </button>
          </div>
        )}
      </div>

      <main className="app-main">
        {renderCurrentView()}
      </main>
    </div>
  );
};

export default App;
