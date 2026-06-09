import { apiClient } from './api-client';
import { UserRegister, UserResponse, TokenResponse, ProfileResponse, ProfileUpdate } from '../types/api';

export const authService = {
  async signup(payload: UserRegister): Promise<UserResponse> {
    const response = await apiClient.post<UserResponse>('/api/v1/auth/signup', payload);
    return response.data;
  },

  async login(username: string, password: string): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async getProfile(): Promise<ProfileResponse> {
    const response = await apiClient.get<ProfileResponse>('/api/v1/auth/profile');
    return response.data;
  },

  async updateProfile(payload: ProfileUpdate): Promise<ProfileResponse> {
    const response = await apiClient.post<ProfileResponse>('/api/v1/auth/profile', payload);
    return response.data;
  },
};
