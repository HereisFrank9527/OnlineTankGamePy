import { WSMessage, TankState, Projectile, GameMap } from '../types';
import { useGameStore, useRoomStore, useUIStore } from '../store';

type MessageHandler = (data: any) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000;
  private isConnecting = false;
  private currentRoomCode: string | null = null;

  connect(roomCode: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Connection already in progress'));
        return;
      }

      this.isConnecting = true;
      this.currentRoomCode = roomCode;

      const tokens = JSON.parse(localStorage.getItem('tokens') || '{}');
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/game/${roomCode}?token=${tokens.access_token}`;
      
      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WSMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.currentRoomCode = null;
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.currentRoomCode = null;
  }

  send(message: WSMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  // Tank control messages
  sendTankStateUpdate(x: number, y: number, rotation: number, velocityX: number, velocityY: number): void {
    this.send({
      type: 'tank_state_update',
      data: {
        x, y, rotation, velocity_x: velocityX, velocity_y: velocityY
      }
    });
  }

  sendFireProjectile(x: number, y: number, rotation: number): void {
    this.send({
      type: 'fire',
      data: { x, y, rotation }
    });
  }

  private scheduleReconnect(): void {
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts);
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
    
    setTimeout(() => {
      this.reconnectAttempts++;
      if (this.currentRoomCode) {
        this.connect(this.currentRoomCode).catch(console.error);
      }
    }, delay);
  }

  private handleMessage(message: WSMessage): void {
    const handlers = this.messageHandlers.get(message.type) || [];
    handlers.forEach(handler => handler(message.data));

    // Handle built-in message types
    switch (message.type) {
      case 'tank_state_update':
        useGameStore.getState().updateTankStates(message.data.tank_states);
        break;
      
      case 'projectile_update':
        useGameStore.getState().updateProjectiles(message.data.projectiles);
        break;
      
      case 'scoreboard_update':
        useGameStore.getState().updateScoreboard(message.data.players);
        break;
      
      case 'player_joined':
        // Refresh room data to get updated member list
        this.refreshRoomData();
        break;
      
      case 'player_left':
        this.refreshRoomData();
        break;
      
      case 'game_started':
        useGameStore.getState().setGameActive(true);
        useUIStore.getState().setCurrentView('game');
        break;
      
      case 'game_ended':
        useGameStore.getState().setGameActive(false);
        // Could show game over screen here
        break;
      
      case 'error':
        useUIStore.getState().showError(message.data.message);
        break;
    }
  }

  private refreshRoomData(): void {
    const { currentRoom, fetchAvailableRooms } = useRoomStore.getState();
    if (currentRoom) {
      // Refresh room data to get updated member list
      fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rooms/${currentRoom.code}`, {
        headers: {
          'Authorization': `Bearer ${JSON.parse(localStorage.getItem('tokens') || '{}').access_token}`,
        },
      })
      .then(response => response.json())
      .then(room => {
        useRoomStore.getState().setCurrentRoom(room);
        if (room.members) {
          useRoomStore.getState().setRoomMembers(room.members);
        }
      })
      .catch(console.error);
    }
  }

  on(type: string, handler: MessageHandler): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)!.push(handler);
  }

  off(type: string, handler: MessageHandler): void {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }
}

export const wsService = new WebSocketService();
