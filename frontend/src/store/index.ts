import { create } from 'zustand';
import { User, AuthTokens, Room, RoomMember, TankState, Projectile } from '../types';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  login: (user: User, tokens: AuthTokens) => void;
  logout: () => void;
  updateUser: (user: User) => void;
}

interface RoomState {
  currentRoom: Room | null;
  availableRooms: Room[];
  roomMembers: RoomMember[];
  isLoading: boolean;
  error: string | null;
  fetchAvailableRooms: () => Promise<void>;
  createRoom: (name: string) => Promise<Room>;
  joinRoom: (roomCode: string) => Promise<void>;
  leaveRoom: () => Promise<void>;
  setReady: (isReady: boolean) => Promise<void>;
  startGame: () => Promise<void>;
  setCurrentRoom: (room: Room | null) => void;
  setRoomMembers: (members: RoomMember[]) => void;
}

interface GameState {
  tankStates: TankState[];
  projectiles: Projectile[];
  gameMap: any;
  isGameActive: boolean;
  scoreboard: Array<{
    player_id: number;
    username: string;
    hp: number;
    kills: number;
  }>;
  updateTankStates: (tankStates: TankState[]) => void;
  updateProjectiles: (projectiles: Projectile[]) => void;
  updateScoreboard: (scoreboard: GameState['scoreboard']) => void;
  setGameMap: (gameMap: any) => void;
  setGameActive: (isActive: boolean) => void;
  resetGame: () => void;
}

interface UIState {
  currentView: 'login' | 'lobby' | 'game';
  setCurrentView: (view: UIState['currentView']) => void;
  showError: (message: string) => void;
  hideError: () => void;
  error: string | null;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  tokens: null,
  isAuthenticated: false,
  login: (user, tokens) => {
    localStorage.setItem('tokens', JSON.stringify(tokens));
    set({ user, tokens, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('tokens');
    set({ user: null, tokens: null, isAuthenticated: false });
  },
  updateUser: (user) => set({ user }),
}));

export const useRoomStore = create<RoomState>((set, get) => ({
  currentRoom: null,
  availableRooms: [],
  roomMembers: [],
  isLoading: false,
  error: null,
  fetchAvailableRooms: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rooms`);
      if (!response.ok) throw new Error('Failed to fetch rooms');
      const rooms = await response.json();
      set({ availableRooms: rooms, isLoading: false });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
    }
  },
  createRoom: async (name: string) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = JSON.parse(localStorage.getItem('tokens') || '{}');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rooms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tokens.access_token}`,
        },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) throw new Error('Failed to create room');
      const room = await response.json();
      set({ currentRoom: room, isLoading: false });
      return room;
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  },
  joinRoom: async (roomCode: string) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = JSON.parse(localStorage.getItem('tokens') || '{}');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rooms/${roomCode}/join`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to join room');
      const room = await response.json();
      set({ currentRoom: room, isLoading: false });
    } catch (error) {
      set({ error: (error as Error).message, isLoading: false });
      throw error;
    }
  },
  leaveRoom: async () => {
    const { currentRoom } = get();
    if (!currentRoom) return;
    
    try {
      const tokens = JSON.parse(localStorage.getItem('tokens') || '{}');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rooms/${currentRoom.code}/leave`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to leave room');
      set({ currentRoom: null, roomMembers: [] });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },
  setReady: async (isReady: boolean) => {
    const { currentRoom } = get();
    if (!currentRoom) return;
    
    try {
      const tokens = JSON.parse(localStorage.getItem('tokens') || '{}');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rooms/${currentRoom.code}/ready/${isReady}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to set ready status');
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },
  startGame: async () => {
    const { currentRoom } = get();
    if (!currentRoom) return;
    
    try {
      const tokens = JSON.parse(localStorage.getItem('tokens') || '{}');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/rooms/${currentRoom.code}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`,
        },
      });
      if (!response.ok) throw new Error('Failed to start game');
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },
  setCurrentRoom: (room) => set({ currentRoom: room }),
  setRoomMembers: (members) => set({ roomMembers: members }),
}));

export const useGameStore = create<GameState>((set) => ({
  tankStates: [],
  projectiles: [],
  gameMap: null,
  isGameActive: false,
  scoreboard: [],
  updateTankStates: (tankStates) => set({ tankStates }),
  updateProjectiles: (projectiles) => set({ projectiles }),
  updateScoreboard: (scoreboard) => set({ scoreboard }),
  setGameMap: (gameMap) => set({ gameMap }),
  setGameActive: (isActive) => set({ isGameActive: isActive }),
  resetGame: () => set({ 
    tankStates: [], 
    projectiles: [], 
    scoreboard: [], 
    isGameActive: false 
  }),
}));

export const useUIStore = create<UIState>((set) => ({
  currentView: 'login',
  error: null,
  setCurrentView: (view) => set({ currentView: view }),
  showError: (message) => set({ error: message }),
  hideError: () => set({ error: null }),
}));
