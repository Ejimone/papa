import apiClient from './client';

// Admin Dashboard
export const getAdminDashboard = async () => {
  try {
    const response = await apiClient.get('/admin/dashboard');
    return response.data;
  } catch (error) {
    console.error('Error fetching admin dashboard:', error);
    throw error;
  }
};

// User Management
export const getAdminUsers = async (page = 1, limit = 10, search = '', role = '') => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(search && { search }),
      ...(role && { role }),
    });
    const response = await apiClient.get(`/admin/users?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin users:', error);
    throw error;
  }
};

export const createUser = async (userData) => {
  try {
    const response = await apiClient.post('/admin/users', userData);
    return response.data;
  } catch (error) {
    console.error('Error creating user:', error);
    throw error;
  }
};

export const updateUser = async (userId, userData) => {
  try {
    const response = await apiClient.put(`/admin/users/${userId}`, userData);
    return response.data;
  } catch (error) {
    console.error('Error updating user:', error);
    throw error;
  }
};

export const deleteUser = async (userId) => {
  try {
    const response = await apiClient.delete(`/admin/users/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting user:', error);
    throw error;
  }
};

// Question Management
export const getAdminQuestions = async (page = 1, limit = 10, search = '', subject = '', difficulty = '', status = '') => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(search && { search }),
      ...(subject && { subject }),
      ...(difficulty && { difficulty }),
      ...(status && { status }),
    });
    const response = await apiClient.get(`/admin/questions?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin questions:', error);
    throw error;
  }
};

export const createQuestion = async (questionData) => {
  try {
    const response = await apiClient.post('/admin/questions', questionData);
    return response.data;
  } catch (error) {
    console.error('Error creating question:', error);
    throw error;
  }
};

export const updateQuestion = async (questionId, questionData) => {
  try {
    const response = await apiClient.put(`/admin/questions/${questionId}`, questionData);
    return response.data;
  } catch (error) {
    console.error('Error updating question:', error);
    throw error;
  }
};

export const deleteQuestion = async (questionId) => {
  try {
    const response = await apiClient.delete(`/admin/questions/${questionId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting question:', error);
    throw error;
  }
};

// Analytics
export const getAdminAnalytics = async (timeRange = '7d', type = 'all') => {
  try {
    const params = new URLSearchParams({
      time_range: timeRange,
      type,
    });
    const response = await apiClient.get(`/admin/analytics?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin analytics:', error);
    throw error;
  }
};

// Database Query
export const executeQuery = async (query, params = {}) => {
  try {
    const response = await apiClient.post('/admin/database/query', {
      query,
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error executing database query:', error);
    throw error;
  }
};

export const getTableSchema = async (tableName) => {
  try {
    const response = await apiClient.get(`/admin/database/schema/${tableName}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching table schema:', error);
    throw error;
  }
};

// Upload Management
export const getAdminUploads = async (page = 1, limit = 10, search = '', fileType = '', status = '') => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(search && { search }),
      ...(fileType && { file_type: fileType }),
      ...(status && { status }),
    });
    const response = await apiClient.get(`/admin/uploads?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching admin uploads:', error);
    throw error;
  }
};

export const reprocessUpload = async (uploadId) => {
  try {
    const response = await apiClient.post(`/admin/uploads/${uploadId}/reprocess`);
    return response.data;
  } catch (error) {
    console.error('Error reprocessing upload:', error);
    throw error;
  }
};

export const deleteUpload = async (uploadId) => {
  try {
    const response = await apiClient.delete(`/admin/uploads/${uploadId}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting upload:', error);
    throw error;
  }
};

// Content Review
export const getContentReview = async (page = 1, limit = 10, type = 'all', status = 'pending') => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      type,
      status,
    });
    const response = await apiClient.get(`/admin/content-review?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching content review:', error);
    throw error;
  }
};

export const approveContent = async (contentId, moderatorNotes = '') => {
  try {
    const response = await apiClient.post(`/admin/content-review/${contentId}/approve`, {
      moderator_notes: moderatorNotes,
    });
    return response.data;
  } catch (error) {
    console.error('Error approving content:', error);
    throw error;
  }
};

export const rejectContent = async (contentId, reason, moderatorNotes = '') => {
  try {
    const response = await apiClient.post(`/admin/content-review/${contentId}/reject`, {
      reason,
      moderator_notes: moderatorNotes,
    });
    return response.data;
  } catch (error) {
    console.error('Error rejecting content:', error);
    throw error;
  }
};

// System Settings
export const getSystemSettings = async () => {
  try {
    const response = await apiClient.get('/admin/settings');
    return response.data;
  } catch (error) {
    console.error('Error fetching system settings:', error);
    throw error;
  }
};

export const updateSystemSettings = async (settings) => {
  try {
    const response = await apiClient.put('/admin/settings', settings);
    return response.data;
  } catch (error) {
    console.error('Error updating system settings:', error);
    throw error;
  }
};

export const resetSystemSettings = async () => {
  try {
    const response = await apiClient.post('/admin/settings/reset');
    return response.data;
  } catch (error) {
    console.error('Error resetting system settings:', error);
    throw error;
  }
};

// System Logs
export const getSystemLogs = async (page = 1, limit = 50, level = 'all', startDate = '', endDate = '') => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      level,
      ...(startDate && { start_date: startDate }),
      ...(endDate && { end_date: endDate }),
    });
    const response = await apiClient.get(`/admin/logs?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching system logs:', error);
    throw error;
  }
};

// Export Data
export const exportData = async (dataType, filters = {}) => {
  try {
    const response = await apiClient.post('/admin/export', {
      data_type: dataType,
      filters,
    });
    return response.data;
  } catch (error) {
    console.error('Error exporting data:', error);
    throw error;
  }
};
