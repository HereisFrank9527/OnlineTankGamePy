export interface User {
  id: number;
  username: string;
  email: string;
  kills: number;
  deaths: number;
  wins: number;
  losses: number;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface Room {
  id: number;
  code: string;
  name: string;
  status: 'waiting' | 'playing' | 'finished';
  max_players: number;
  created_at: string;
  members?: RoomMember[];
}

export interface RoomMember {
  id: number;
  player: User;
  is_ready: boolean;
  joined_at: string;
}

export interface TankState {
  id: number;
  player_id: number;
  room_id: number;
  x: number;
  y: number;
  rotation: number;
  hp: number;
  velocity_x: number;
  velocity_y: number;
  is_alive: boolean;
}

export interface Projectile {
  id: number;
  room_id: number;
  player_id: number;
  x: number;
  y: number;
  velocity_x: number;
  velocity_y: number;
  damage: number;
  created_at: string;
}

export interface GameMap {
  width: number;
  height: number;
  obstacles: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
  }>;
  spawnPoints: Array<{
    x: number;
    y: number;
  }>;
  powerUps: Array<{
    x: number;
    y: number;
    type: string;
  }>;
}

// WebSocket Message Types
export interface WSMessage {
  type: string;
  data: any;
}

export interface TankStateUpdate extends WSMessage {
  type: 'tank_state_update';
  data: {
    tank_states: TankState[];
  };
}

export interface ProjectileUpdate extends WSMessage {
  type: 'projectile_update';
  data: {
    projectiles: Projectile[];
  };
}

export interface ScoreboardUpdate extends WSMessage {
  type: 'scoreboard_update';
  data: {
    players: Array<{
      player_id: number;
      username: string;
      hp: number;
      kills: number;
    }>;
  };
}

export interface PlayerJoined extends WSMessage {
  type: 'player_joined';
  data: {
    player: User;
  };
}

export interface PlayerLeft extends WSMessage {
  type: 'player_left';
  data: {
    player_id: number;
  };
}

export interface GameStarted extends WSMessage {
  type: 'game_started';
  data: {};
}

export interface GameEnded extends WSMessage {
  type: 'game_ended';
  data: {
    winner?: User;
  };
}

export interface ErrorMessage extends WSMessage {
  type: 'error';
  data: {
    message: string;
  };
}
