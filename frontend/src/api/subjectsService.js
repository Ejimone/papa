import apiClient from './client';

export const subjectsService = {
  // Subject Management
  async getSubjects(params = {}) {
    try {
      const response = await apiClient.get('/subjects', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getSubjectsWithTopics() {
    try {
      const response = await apiClient.get('/subjects/with-topics');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getSubjectById(subjectId) {
    try {
      const response = await apiClient.get(`/subjects/${subjectId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async createSubject(subjectData) {
    try {
      const response = await apiClient.post('/subjects', subjectData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateSubject(subjectId, subjectData) {
    try {
      const response = await apiClient.put(`/subjects/${subjectId}`, subjectData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async deleteSubject(subjectId) {
    try {
      const response = await apiClient.delete(`/subjects/${subjectId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Topic Management
  async getTopicsBySubject(subjectId, params = {}) {
    try {
      const response = await apiClient.get(`/subjects/${subjectId}/topics`, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getTopicsWithQuestionCount(subjectId) {
    try {
      const response = await apiClient.get(`/subjects/${subjectId}/topics/with-question-count`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async createTopic(subjectId, topicData) {
    try {
      const response = await apiClient.post(`/subjects/${subjectId}/topics`, topicData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getTopicById(topicId) {
    try {
      const response = await apiClient.get(`/subjects/topics/${topicId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async updateTopic(topicId, topicData) {
    try {
      const response = await apiClient.put(`/subjects/topics/${topicId}`, topicData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async deleteTopic(topicId) {
    try {
      const response = await apiClient.delete(`/subjects/topics/${topicId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Search
  async searchSubjects(query, params = {}) {
    try {
      const response = await apiClient.get('/subjects/search', {
        params: { q: query, ...params }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async searchTopics(query, params = {}) {
    try {
      const response = await apiClient.get('/subjects/topics/search', {
        params: { q: query, ...params }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async searchSubjectsAndTopics(query, params = {}) {
    try {
      const response = await apiClient.get('/search/subjects-topics', {
        params: { q: query, ...params }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Utility Methods
  async getSubjectStatistics(subjectId) {
    try {
      const response = await apiClient.get(`/subjects/${subjectId}/statistics`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getPopularSubjects() {
    try {
      const response = await apiClient.get('/subjects/popular');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
}; 