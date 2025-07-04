import apiClient from './client';

export const analyticsService = {
  // Dashboard & Overview
  async getDashboardData() {
    try {
      const response = await apiClient.get('/analytics/dashboard');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getUserAnalytics(params = {}) {
    try {
      const response = await apiClient.get('/analytics/user-analytics', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getPerformanceTrends(params = {}) {
    try {
      const response = await apiClient.get('/analytics/performance-trends', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getWeeklyActivity() {
    try {
      const response = await apiClient.get('/analytics/weekly-activity');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Detailed Analytics
  async getSubjectPerformance(params = {}) {
    try {
      const response = await apiClient.get('/analytics/subject-performance', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getLearningInsights() {
    try {
      const response = await apiClient.get('/analytics/learning-insights');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getComparisonData(params = {}) {
    try {
      const response = await apiClient.get('/analytics/comparison', { params });
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

  async getLeaderboard(params = {}) {
    try {
      const response = await apiClient.get('/users/leaderboard', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Reporting & Export
  async generateReport(reportConfig) {
    try {
      const response = await apiClient.post('/analytics/reports/generate', reportConfig);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async exportData(format = 'json', params = {}) {
    try {
      const response = await apiClient.get('/analytics/export', {
        params: { format, ...params },
        responseType: format === 'csv' ? 'blob' : 'json'
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Event Tracking
  async trackEvent(eventData) {
    try {
      const response = await apiClient.post('/analytics/events', eventData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Custom Analytics Queries
  async getPerformanceByTimeRange(startDate, endDate) {
    try {
      const response = await apiClient.get('/analytics/performance-trends', {
        params: {
          start_date: startDate,
          end_date: endDate
        }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getSubjectProgress(subjectId) {
    try {
      const response = await apiClient.get('/analytics/subject-performance', {
        params: { subject_id: subjectId }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getAccuracyTrends(days = 30) {
    try {
      const response = await apiClient.get('/analytics/performance-trends', {
        params: { 
          metric: 'accuracy',
          days: days
        }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getStudyTimeAnalysis(period = 'week') {
    try {
      const response = await apiClient.get('/analytics/user-analytics', {
        params: { period }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
}; 