import React, { useEffect, useRef, useState } from 'react';
import { useAuthStore, useRoomStore, useGameStore } from '../store';
import { wsService } from '../services/websocket';
import { GameEngine } from '../game/GameEngine';
import { TankState, Projectile } from '../types';
import './GameView.css';

const GameView: React.FC = () => {
  const gameCanvasRef = useRef<HTMLDivElement>(null);
  const gameEngineRef = useRef<GameEngine | null>(null);
  const [isGameEngineReady, setIsGameEngineReady] = useState(false);
  
  const { user } = useAuthStore();
  const { currentRoom } = useRoomStore();
  const { 
    tankStates, 
    projectiles, 
    scoreboard, 
    isGameActive,
    updateTankStates, 
    updateProjectiles, 
    updateScoreboard,
    setGameActive,
    resetGame
  } = useGameStore();

  useEffect(() => {
    if (gameCanvasRef.current && user && currentRoom) {
      // Initialize game engine
      gameEngineRef.current = new GameEngine(gameCanvasRef.current);
      
      // Set up game engine callbacks
      gameEngineRef.current.setPlayerId(user.id);
      
      gameEngineRef.current.setOnTankStateChange(
        (x: number, y: number, rotation: number, velocityX: number, velocityY: number) => {
          if (wsService.isConnected()) {
            wsService.sendTankStateUpdate(x, y, rotation, velocityX, velocityY);
          }
        }
      );
      
      gameEngineRef.current.setOnFireProjectile(
        (x: number, y: number, rotation: number) => {
          if (wsService.isConnected()) {
            wsService.sendFireProjectile(x, y, rotation);
          }
        }
      );

      setIsGameEngineReady(true);

      return () => {
        if (gameEngineRef.current) {
          gameEngineRef.current.destroy();
          gameEngineRef.current = null;
        }
        setIsGameEngineReady(false);
      };
    }
  }, [user, currentRoom]);

  // Update game engine with tank states
  useEffect(() => {
    if (isGameEngineReady && gameEngineRef.current) {
      gameEngineRef.current.updateTankStates(tankStates);
    }
  }, [tankStates, isGameEngineReady]);

  // Update game engine with projectiles
  useEffect(() => {
    if (isGameEngineReady && gameEngineRef.current) {
      gameEngineRef.current.updateProjectiles(projectiles);
    }
  }, [projectiles, isGameEngineReady]);

  // Set up WebSocket message handlers
  useEffect(() => {
    if (!currentRoom) return;

    const handleTankStateUpdate = (data: { tank_states: TankState[] }) => {
      updateTankStates(data.tank_states);
    };

    const handleProjectileUpdate = (data: { projectiles: Projectile[] }) => {
      updateProjectiles(data.projectiles);
    };

    const handleScoreboardUpdate = (data: { players: any[] }) => {
      updateScoreboard(data.players);
    };

    const handleGameStarted = () => {
      setGameActive(true);
    };

    const handleGameEnded = (data: { winner?: any }) => {
      setGameActive(false);
      // Could show game over modal here
      console.log('Game ended:', data.winner ? `${data.winner.username} won!` : 'Game ended');
    };

    const handleError = (data: { message: string }) => {
      console.error('Game error:', data.message);
    };

    // Register WebSocket handlers
    wsService.on('tank_state_update', handleTankStateUpdate);
    wsService.on('projectile_update', handleProjectileUpdate);
    wsService.on('scoreboard_update', handleScoreboardUpdate);
    wsService.on('game_started', handleGameStarted);
    wsService.on('game_ended', handleGameEnded);
    wsService.on('error', handleError);

    return () => {
      // Clean up WebSocket handlers
      wsService.off('tank_state_update', handleTankStateUpdate);
      wsService.off('projectile_update', handleProjectileUpdate);
      wsService.off('scoreboard_update', handleScoreboardUpdate);
      wsService.off('game_started', handleGameStarted);
      wsService.off('game_ended', handleGameEnded);
      wsService.off('error', handleError);
    };
  }, [currentRoom, updateTankStates, updateProjectiles, updateScoreboard, setGameActive]);

  const handleLeaveGame = () => {
    wsService.disconnect();
    resetGame();
    // Navigate back to lobby
    window.location.href = '/lobby';
  };

  const getPlayerTank = () => {
    return tankStates.find(tank => tank.player_id === user?.id);
  };

  const getPlayerScore = () => {
    return scoreboard.find(player => player.player_id === user?.id);
  };

  if (!currentRoom) {
    return (
      <div className="game-container">
        <div className="game-error">
          <h2>No active room</h2>
          <p>Please return to the lobby to join a game.</p>
          <button onClick={handleLeaveGame}>Back to Lobby</button>
        </div>
      </div>
    );
  }

  return (
    <div className="game-container">
      <div className="game-header">
        <div className="game-info">
          <h2>{currentRoom.name}</h2>
          <p>Room Code: <span className="room-code">{currentRoom.code}</span></p>
        </div>
        <div className="game-controls">
          <button onClick={handleLeaveGame} className="leave-game-btn">
            Leave Game
          </button>
        </div>
      </div>

      <div className="game-layout">
        <div className="game-canvas-container">
          <div ref={gameCanvasRef} className="game-canvas" />
          
          {!isGameActive && (
            <div className="game-overlay">
              <div className="waiting-message">
                <h3>Waiting for game to start...</h3>
                <div className="spinner"></div>
              </div>
            </div>
          )}
        </div>

        <div className="game-sidebar">
          <div className="scoreboard">
            <h3>Scoreboard</h3>
            <div className="scoreboard-list">
              {scoreboard.length === 0 ? (
                <p className="no-data">No players in game</p>
              ) : (
                scoreboard
                  .sort((a, b) => b.kills - a.kills || b.hp - a.hp)
                  .map((player, index) => (
                    <div 
                      key={player.player_id} 
                      className={`scoreboard-item ${player.player_id === user?.id ? 'current-player' : ''}`}
                    >
                      <div className="player-rank">#{index + 1}</div>
                      <div className="player-info">
                        <div className="player-name">{player.username}</div>
                        <div className="player-stats">
                          HP: {player.hp} | Kills: {player.kills}
                        </div>
                      </div>
                    </div>
                  ))
              )}
            </div>
          </div>

          <div className="game-stats">
            <h3>Game Stats</h3>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-label">Active Players</span>
                <span className="stat-value">{tankStates.filter(tank => tank.is_alive).length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Projectiles</span>
                <span className="stat-value">{projectiles.length}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Game Status</span>
                <span className={`stat-value status-${isGameActive ? 'playing' : 'waiting'}`}>
                  {isGameActive ? 'Active' : 'Waiting'}
                </span>
              </div>
            </div>
          </div>

          {getPlayerTank() && (
            <div className="player-stats">
              <h3>Your Tank</h3>
              <div className="tank-info">
                <div className="tank-health">
                  <div className="health-bar">
                    <div 
                      className="health-fill" 
                      style={{ width: `${Math.max(0, getPlayerTank()!.hp)}%` }}
                    />
                  </div>
                  <span className="health-text">
                    {getPlayerTank()!.hp} HP
                  </span>
                </div>
                <div className="tank-position">
                  X: {Math.round(getPlayerTank()!.x)} | Y: {Math.round(getPlayerTank()!.y)}
                </div>
                <div className="tank-rotation">
                  Rotation: {Math.round(getPlayerTank()!.rotation * 180 / Math.PI)}°
                </div>
              </div>
            </div>
          )}

          <div className="controls-help">
            <h3>Controls</h3>
            <div className="control-item">
              <kbd>W</kbd> or <kbd>↑</kbd> Move Up
            </div>
            <div className="control-item">
              <kbd>S</kbd> or <kbd>↓</kbd> Move Down
            </div>
            <div className="control-item">
              <kbd>A</kbd> or <kbd>←</kbd> Rotate Left
            </div>
            <div className="control-item">
              <kbd>D</kbd> or <kbd>→</kbd> Rotate Right
            </div>
            <div className="control-item">
              <kbd>Space</kbd> Fire
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameView;
