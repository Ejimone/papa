import apiClient from './client';

export const userService = {
  // User Profile Management
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/users/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateCurrentUser(userData) {
    try {
      const response = await apiClient.put('/users/me', userData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async changePassword(passwordData) {
    try {
      const response = await apiClient.put('/users/me/password', passwordData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // User Statistics
  async getUserStatistics() {
    try {
      const response = await apiClient.get('/users/me/statistics');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Leaderboard
  async getLeaderboard(params = {}) {
    try {
      const response = await apiClient.get('/users/leaderboard', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getAccuracyLeaderboard(days = 30, limit = 10) {
    try {
      const response = await apiClient.get('/users/leaderboard', {
        params: {
          metric: 'accuracy',
          days,
          limit
        }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getVolumeLeaderboard(days = 30, limit = 10) {
    try {
      const response = await apiClient.get('/users/leaderboard', {
        params: {
          metric: 'volume',
          days,
          limit
        }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // User Achievements and Progress
  async getUserAchievements() {
    try {
      const response = await apiClient.get('/users/me/achievements');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getUserStreak() {
    try {
      const response = await apiClient.get('/users/me/streak');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // User Settings and Preferences
  async getUserSettings() {
    try {
      const response = await apiClient.get('/users/me/settings');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateUserSettings(settings) {
    try {
      const response = await apiClient.put('/users/me/settings', settings);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Study Goals and Targets
  async getStudyGoals() {
    try {
      const response = await apiClient.get('/users/me/goals');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async setStudyGoals(goals) {
    try {
      const response = await apiClient.post('/users/me/goals', goals);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateStudyGoal(goalId, goalData) {
    try {
      const response = await apiClient.put(`/users/me/goals/${goalId}`, goalData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Account Management
  async deleteAccount() {
    try {
      const response = await apiClient.delete('/users/me');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async requestAccountDeletion() {
    try {
      const response = await apiClient.post('/users/me/request-deletion');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async exportUserData(format = 'json') {
    try {
      const response = await apiClient.get('/users/me/export', {
        params: { format },
        responseType: format === 'csv' ? 'blob' : 'json'
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
}; 