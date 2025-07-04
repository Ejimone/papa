import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_CONFIG } from "../config/api";

// Create axios instance
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: API_CONFIG.TIMEOUT,
});

// Token management
const TOKEN_KEY = "@auth_token";
const REFRESH_TOKEN_KEY = "@refresh_token";

let currentToken = null;

export const tokenManager = {
  async setToken(token) {
    currentToken = token;
    await AsyncStorage.setItem(TOKEN_KEY, token);
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  },

  async setRefreshToken(refreshToken) {
    await AsyncStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },

  async getToken() {
    if (currentToken) return currentToken;
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    if (token) {
      currentToken = token;
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    }
    return token;
  },

  async getRefreshToken() {
    return await AsyncStorage.getItem(REFRESH_TOKEN_KEY);
  },

  async clearTokens() {
    currentToken = null;
    await AsyncStorage.multiRemove([TOKEN_KEY, REFRESH_TOKEN_KEY]);
    delete apiClient.defaults.headers.common["Authorization"];
  },
};

// Initialize token on app start
tokenManager.getToken();

// Request interceptor
apiClient.interceptors.request.use(
  async (config) => {
    const token = await tokenManager.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url} with auth token`);
    } else {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url} WITHOUT auth token`);
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
    return response;
  },
  async (error) => {
    console.error(`API Error: ${error.response?.status || 'Network Error'} ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.message);
    
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('Received 401, attempting token refresh...');
      originalRequest._retry = true;

      try {
        const refreshToken = await tokenManager.getRefreshToken();
        if (refreshToken) {
          console.log('Attempting to refresh token...');
          const response = await axios.post(`${API_CONFIG.BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          await tokenManager.setToken(access_token);
          console.log('Token refreshed successfully');

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        } else {
          console.log('No refresh token available');
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Refresh failed, clear tokens and redirect to login
        await tokenManager.clearTokens();
        // You might want to dispatch a logout action here
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
