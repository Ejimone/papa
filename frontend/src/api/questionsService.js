import apiClient from './client';

export const questionsService = {
  // Browse & Search Questions
  async getQuestions(params = {}) {
    try {
      const response = await apiClient.get('/questions', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async searchQuestions(params = {}) {
    try {
      const response = await apiClient.get('/questions/search', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getRandomQuestions(params = {}) {
    try {
      const response = await apiClient.get('/questions/random', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Question Details
  async getQuestionById(questionId) {
    try {
      const response = await apiClient.get(`/questions/${questionId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getQuestionForPractice(questionId) {
    try {
      const response = await apiClient.get(`/questions/${questionId}/public`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getSimilarQuestions(questionId, limit = 5) {
    try {
      const response = await apiClient.get(`/questions/${questionId}/similar`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Question Management (Create, Update, Delete)
  async createQuestion(questionData) {
    try {
      const response = await apiClient.post('/questions', questionData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async createQuestionsInBulk(questionsData) {
    try {
      const response = await apiClient.post('/questions/bulk', questionsData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateQuestion(questionId, questionData) {
    try {
      const response = await apiClient.put(`/questions/${questionId}`, questionData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async deleteQuestion(questionId) {
    try {
      const response = await apiClient.delete(`/questions/${questionId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Metadata Management
  async addQuestionMetadata(questionId, metadata) {
    try {
      const response = await apiClient.post(`/questions/${questionId}/metadata`, metadata);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async addQuestionExplanation(questionId, explanation) {
    try {
      const response = await apiClient.post(`/questions/${questionId}/explanations`, explanation);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async addQuestionHints(questionId, hints) {
    try {
      const response = await apiClient.post(`/questions/${questionId}/hints`, hints);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Advanced Search with Filters
  async searchWithFilters(searchQuery, filters = {}) {
    try {
      const params = {
        q: searchQuery,
        ...filters
      };
      const response = await apiClient.get('/search/questions', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Search Suggestions and Autocomplete
  async getSearchSuggestions(query) {
    try {
      const response = await apiClient.get('/search/suggestions', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getAutocompleteResults(query) {
    try {
      const response = await apiClient.get('/search/autocomplete', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Popular and Trending
  async getPopularQuestions() {
    try {
      const response = await apiClient.get('/search/popular');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getTrendingQuestions() {
    try {
      const response = await apiClient.get('/search/trending');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
}; 