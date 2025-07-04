import apiClient, { tokenManager } from './client';

export const authService = {
  // User Registration
  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register', userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // User Login
  async login(credentials) {
    try {
      const response = await apiClient.post('/auth/login', credentials);
      const { access_token, refresh_token, ...userData } = response.data;
      
      // Store tokens
      await tokenManager.setToken(access_token);
      await tokenManager.setRefreshToken(refresh_token);
      
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Alternative login endpoint
  async getToken(credentials) {
    try {
      const response = await apiClient.post('/auth/token', credentials);
      const { access_token, refresh_token } = response.data;
      
      await tokenManager.setToken(access_token);
      await tokenManager.setRefreshToken(refresh_token);
      
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Refresh Token
  async refreshToken() {
    try {
      const refreshToken = await tokenManager.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshToken,
      });

      const { access_token } = response.data;
      await tokenManager.setToken(access_token);
      
      return response.data;
    } catch (error) {
      await tokenManager.clearTokens();
      throw error.response?.data || error.message;
    }
  },

  // Logout
  async logout() {
    try {
      // Call logout endpoint if available
      await apiClient.post('/auth/logout');
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error);
    } finally {
      // Always clear local tokens
      await tokenManager.clearTokens();
    }
  },

  // Check if user is authenticated
  async isAuthenticated() {
    const token = await tokenManager.getToken();
    return !!token;
  },

  // Get current token
  async getCurrentToken() {
    return await tokenManager.getToken();
  },
}; 