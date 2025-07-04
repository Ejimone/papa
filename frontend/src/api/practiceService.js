import apiClient from './client';

export const practiceService = {
  // Practice Session Management
  async createPracticeSession(sessionConfig) {
    try {
      const response = await apiClient.post('/practice/sessions', sessionConfig);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getPracticeSessions(params = {}) {
    try {
      const response = await apiClient.get('/practice/sessions', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getPracticeSession(sessionId) {
    try {
      const response = await apiClient.get(`/practice/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async completePracticeSession(sessionId, sessionData = {}) {
    try {
      const response = await apiClient.put(`/practice/sessions/${sessionId}/complete`, sessionData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Question Attempts
  async submitAttempt(attemptData) {
    try {
      const response = await apiClient.post('/practice/attempts', attemptData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getAttempts(params = {}) {
    try {
      const response = await apiClient.get('/practice/attempts', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getAttemptById(attemptId) {
    try {
      const response = await apiClient.get(`/practice/attempts/${attemptId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Bookmarks Management
  async bookmarkQuestion(questionId) {
    try {
      const response = await apiClient.post('/practice/bookmarks', {
        question_id: questionId
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async removeBookmark(questionId) {
    try {
      const response = await apiClient.delete(`/practice/bookmarks/${questionId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getBookmarks(params = {}) {
    try {
      const response = await apiClient.get('/practice/bookmarks', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async searchBookmarks(query, params = {}) {
    try {
      const response = await apiClient.get('/search/bookmarks', {
        params: { q: query, ...params }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Progress Tracking
  async getProgress(params = {}) {
    try {
      const response = await apiClient.get('/practice/progress', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getProgressSummary() {
    try {
      const response = await apiClient.get('/practice/progress/summary');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // User Profile & Preferences
  async getUserProfile() {
    try {
      const response = await apiClient.get('/practice/profile');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateUserProfile(profileData) {
    try {
      const response = await apiClient.put('/practice/profile', profileData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getUserPreferences() {
    try {
      const response = await apiClient.get('/practice/preferences');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateUserPreferences(preferences) {
    try {
      const response = await apiClient.put('/practice/preferences', preferences);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Quick Practice Flow
  async startQuickPractice(subject, options = {}) {
    try {
      const sessionConfig = {
        session_type: 'quick_practice',
        subject_id: subject,
        question_count: options.questionCount || 10,
        difficulty_level: options.difficulty || 'mixed',
        ...options
      };
      return await this.createPracticeSession(sessionConfig);
    } catch (error) {
      throw error;
    }
  },

  // Timed Practice
  async startTimedPractice(subject, timeLimit, options = {}) {
    try {
      const sessionConfig = {
        session_type: 'timed',
        subject_id: subject,
        time_limit_minutes: timeLimit,
        question_count: options.questionCount || 20,
        difficulty_level: options.difficulty || 'mixed',
        ...options
      };
      return await this.createPracticeSession(sessionConfig);
    } catch (error) {
      throw error;
    }
  },

  // Mock Test
  async startMockTest(subject, options = {}) {
    try {
      const sessionConfig = {
        session_type: 'mock_test',
        subject_id: subject,
        question_count: options.questionCount || 50,
        time_limit_minutes: options.timeLimit || 120,
        difficulty_level: 'mixed',
        ...options
      };
      return await this.createPracticeSession(sessionConfig);
    } catch (error) {
      throw error;
    }
  },
}; 