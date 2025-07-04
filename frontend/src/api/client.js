import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_BASE_URL = "http://172.16.0.58:4321/api/v1";

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
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
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = await tokenManager.getRefreshToken();
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token } = response.data;
          await tokenManager.setToken(access_token);

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        await tokenManager.clearTokens();
        // You might want to dispatch a logout action here
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
