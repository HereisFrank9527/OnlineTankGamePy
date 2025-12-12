import axios from 'axios';
import { User, AuthTokens, LoginRequest, RegisterRequest, Room } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private api;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use((config) => {
      const tokens = localStorage.getItem('tokens');
      if (tokens) {
        const { access_token } = JSON.parse(tokens);
        config.headers.Authorization = `Bearer ${access_token}`;
      }
      return config;
    });

    // Add response interceptor to handle 401 errors
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('tokens');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async login(credentials: LoginRequest): Promise<{ user: User; tokens: AuthTokens }> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await this.api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return {
      user: response.data.user,
      tokens: {
        access_token: response.data.access_token,
        token_type: response.data.token_type,
      },
    };
  }

  async register(userData: RegisterRequest): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await this.api.post('/auth/register', userData);
    
    return {
      user: response.data.user,
      tokens: {
        access_token: response.data.access_token,
        token_type: response.data.token_type,
      },
    };
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  async getRooms(): Promise<Room[]> {
    const response = await this.api.get('/rooms');
    return response.data;
  }

  async getRoom(roomCode: string): Promise<Room> {
    const response = await this.api.get(`/rooms/${roomCode}`);
    return response.data;
  }

  async createRoom(name: string): Promise<Room> {
    const response = await this.api.post('/rooms', { name });
    return response.data;
  }

  async joinRoom(roomCode: string): Promise<Room> {
    const response = await this.api.post(`/rooms/${roomCode}/join`);
    return response.data;
  }

  async leaveRoom(roomCode: string): Promise<void> {
    await this.api.post(`/rooms/${roomCode}/leave`);
  }

  async setReady(roomCode: string, isReady: boolean): Promise<void> {
    await this.api.post(`/rooms/${roomCode}/ready/${isReady}`);
  }

  async startGame(roomCode: string): Promise<void> {
    await this.api.post(`/rooms/${roomCode}/start`);
  }

  getAuthHeaders() {
    const tokens = localStorage.getItem('tokens');
    if (tokens) {
      const { access_token } = JSON.parse(tokens);
      return { Authorization: `Bearer ${access_token}` };
    }
    return {};
  }
}

export const apiService = new ApiService();
