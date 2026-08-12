import api from './api';

export type LoginCredentials = {
  email: string;
  password: string;
};

export type RegisterData = {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
};

export type User = {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Simulated login for demo purposes
    return {
      access_token: 'demo-token-' + Date.now(),
      token_type: 'Bearer',
      expires_in: 3600,
    };
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    // Simulated registration for demo purposes
    return {
      access_token: 'demo-token-' + Date.now(),
      token_type: 'Bearer',
      expires_in: 3600,
    };
  },

  async getCurrentUser(): Promise<User> {
    // Simulated user data for demo purposes
    return {
      id: '1',
      email: 'demo@example.com',
      username: 'demo',
      first_name: 'Demo',
      last_name: 'User',
      role: 'admin',
      is_active: true,
      is_verified: true,
      created_at: new Date().toISOString(),
    };
  },

  logout() {
    localStorage.removeItem('token');
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  },

  setToken(token: string) {
    localStorage.setItem('token', token);
  },
};
