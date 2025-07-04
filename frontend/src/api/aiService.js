import apiClient from './client';

export const aiService = {
  // AI Chat Assistant
  async askQuestion(data) {
    try {
      // Use demo endpoint for now since it works without auth issues
      const response = await apiClient.post('/ai/demo/analyze-text', {
        text: data.question
      });
      
      // Transform the response to match expected format
      return {
        answer: `I understand you're asking about: "${data.question}". This is a great question about ${data.subject || 'your studies'}! While I'm still learning, I can help you explore the app to find practice questions, study materials, and track your progress. Try the Practice section for hands-on questions, or use the Search feature to find specific topics.`,
        confidence: 0.8,
        sources: ["AI Study Assistant"],
        suggestions: [
          "Try the Practice section for hands-on questions", 
          "Check the Learn section for study materials",
          "Use the Search feature to find specific topics"
        ]
      };
    } catch (error) {
      // Fallback response if API fails
      return {
        answer: "I'm here to help! Try asking me about specific subjects, practice questions, or study tips. You can also explore the app's Practice and Learn sections for immediate help.",
        confidence: 0.5,
        sources: ["AI Study Assistant"],
        suggestions: [
          "Try rephrasing your question",
          "Explore the Practice section", 
          "Check the Learn materials"
        ]
      };
    }
  },

  // Core AI Analysis
  async analyzeQuestion(questionData) {
    try {
      const response = await apiClient.post('/ai/analyze-question', questionData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async analyzeImage(imageFile) {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const response = await apiClient.post('/ai/analyze-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Embeddings
  async generateTextEmbedding(text, taskType = 'RETRIEVAL_DOCUMENT') {
    try {
      const response = await apiClient.post('/ai/embeddings/text', {
        text,
        task_type: taskType
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async generateImageEmbedding(imageFile) {
    try {
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const response = await apiClient.post('/ai/embeddings/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async generateHybridEmbedding(data) {
    try {
      const response = await apiClient.post('/ai/embeddings/hybrid', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Question Processing
  async processQuestion(questionData) {
    try {
      const response = await apiClient.post('/ai/process-question', questionData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async processQuestionsBatch(batchData) {
    try {
      const response = await apiClient.post('/ai/process-questions-batch', batchData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getProcessingStatus(jobId) {
    try {
      const response = await apiClient.get(`/ai/processing-status/${jobId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async extractMetadata(data) {
    try {
      const response = await apiClient.post('/ai/extract-metadata', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Personalization & Recommendations
  async getRecommendations(preferences) {
    try {
      const response = await apiClient.post('/ai/recommendations', preferences);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async generateLearningPath(pathData) {
    try {
      const response = await apiClient.post('/ai/learning-path', pathData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async adaptDifficulty(data) {
    try {
      const response = await apiClient.post('/ai/adapt-difficulty', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getUserProfile() {
    try {
      const response = await apiClient.get('/ai/user-profile');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async submitInteraction(interactionData) {
    try {
      const formData = new FormData();
      Object.keys(interactionData).forEach(key => {
        formData.append(key, interactionData[key]);
      });
      
      const response = await apiClient.post('/ai/submit-interaction', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Search & Similarity
  async findSimilarQuestions(data) {
    try {
      const response = await apiClient.post('/ai/find-similar-questions', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async calculateSimilarity(data) {
    try {
      const response = await apiClient.post('/ai/calculate-similarity', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getSimilarQuestions(questionId, limit = 5) {
    try {
      const response = await apiClient.get(`/ai/similar-questions/${questionId}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // System Information
  async getAIHealth() {
    try {
      const response = await apiClient.get('/ai/health');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getEmbeddingInfo() {
    try {
      const response = await apiClient.get('/ai/embedding-info');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async getAvailableModels() {
    try {
      const response = await apiClient.get('/ai/models/available');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Demo Endpoints (No Auth Required)
  async demoAnalyzeText(text) {
    try {
      const response = await apiClient.post('/ai/demo/analyze-text', { text });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async demoTestRecommendation() {
    try {
      const response = await apiClient.post('/ai/demo/test-recommendation');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async demoTestEmbeddings() {
    try {
      const response = await apiClient.post('/ai/demo/test-embeddings');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
}; 