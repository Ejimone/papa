import apiClient from './client';

// Upload service for handling file uploads
export const uploadService = {
  // Upload a single image
  uploadImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Upload a single document
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/upload/document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Upload multiple files
  uploadMultipleFiles: async (files) => {
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`files`, file);
    });
    
    const response = await apiClient.post('/upload/multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Upload question with files
  uploadQuestionWithFiles: async (questionData) => {
    const formData = new FormData();
    
    // Add question data
    if (questionData.title) formData.append('title', questionData.title);
    if (questionData.content) formData.append('content', questionData.content);
    if (questionData.answer) formData.append('answer', questionData.answer);
    if (questionData.question_type) formData.append('question_type', questionData.question_type);
    if (questionData.difficulty_level) formData.append('difficulty_level', questionData.difficulty_level);
    if (questionData.subject_id) formData.append('subject_id', questionData.subject_id);
    if (questionData.topic_id) formData.append('topic_id', questionData.topic_id);
    if (questionData.points) formData.append('points', questionData.points);
    if (questionData.time_limit) formData.append('time_limit', questionData.time_limit);
    if (questionData.source) formData.append('source', questionData.source);
    if (questionData.tags) formData.append('tags', questionData.tags);
    
    // Add options if they exist
    if (questionData.options && questionData.options.length > 0) {
      formData.append('options', JSON.stringify(questionData.options));
    }
    
    // Add files
    if (questionData.images && questionData.images.length > 0) {
      questionData.images.forEach((image) => {
        formData.append('images', image);
      });
    }
    
    if (questionData.documents && questionData.documents.length > 0) {
      questionData.documents.forEach((document) => {
        formData.append('documents', document);
      });
    }
    
    const response = await apiClient.post('/questions/upload-with-files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Upload course materials
  uploadCourseMaterials: async (materialsData) => {
    const formData = new FormData();
    
    // Add course material metadata
    formData.append('subject_id', materialsData.subject_id);
    formData.append('title', materialsData.title);
    if (materialsData.topic_id) formData.append('topic_id', materialsData.topic_id);
    if (materialsData.description) formData.append('description', materialsData.description);
    if (materialsData.material_type) formData.append('material_type', materialsData.material_type);
    if (materialsData.tags) formData.append('tags', materialsData.tags);
    
    // Add boolean flags
    formData.append('enable_rag', materialsData.enable_rag ? 'true' : 'false');
    formData.append('auto_extract_questions', materialsData.auto_extract_questions ? 'true' : 'false');
    
    // Add files
    if (materialsData.files && materialsData.files.length > 0) {
      materialsData.files.forEach((file) => {
        formData.append('files', file);
      });
    }
    
    const response = await apiClient.post('/course-materials/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Upload questions batch
  uploadQuestionsBatch: async (files, subjectId, autoProcess = true) => {
    const formData = new FormData();
    
    formData.append('subject_id', subjectId);
    formData.append('auto_process', autoProcess ? 'true' : 'false');
    
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    const response = await apiClient.post('/questions/upload-batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  // Get course materials
  getCourseMaterials: async (filters = {}) => {
    const params = new URLSearchParams();
    
    if (filters.subject_id) params.append('subject_id', filters.subject_id);
    if (filters.topic_id) params.append('topic_id', filters.topic_id);
    if (filters.material_type) params.append('material_type', filters.material_type);
    if (filters.skip) params.append('skip', filters.skip);
    if (filters.limit) params.append('limit', filters.limit);
    
    const response = await apiClient.get(`/course-materials/materials?${params}`);
    return response.data;
  },
};

export default uploadService;
