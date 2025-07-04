// API Client
export { default as apiClient, tokenManager } from './client';

// API Services
export { authService } from './authService';
export { questionsService } from './questionsService';
export { practiceService } from './practiceService';
export { subjectsService } from './subjectsService';
export { analyticsService } from './analyticsService';
export { aiService } from './aiService';
export { userService } from './userService';
export * as adminService from './adminService';

// For backward compatibility and convenience
export * from './authService';
export * from './questionsService';
export * from './practiceService';
export * from './subjectsService';
export * from './analyticsService';
export * from './aiService';
export * from './userService';
export * from './adminService';

// Utility function to check API health
export const checkAPIHealth = async () => {
  try {
    const { default: apiClient } = await import('./client');
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.warn('API health check failed:', error);
    return { status: 'error', message: error.message };
  }
};

// Centralized API object factory function
export const createAPI = async () => {
  const { authService } = await import('./authService');
  const { questionsService } = await import('./questionsService');
  const { practiceService } = await import('./practiceService');
  const { subjectsService } = await import('./subjectsService');
  const { analyticsService } = await import('./analyticsService');
  const { aiService } = await import('./aiService');
  const { userService } = await import('./userService');

  return {
    auth: authService,
    questions: questionsService,
    practice: practiceService,
    subjects: subjectsService,
    analytics: analyticsService,
    ai: aiService,
    user: userService,
  };
};

// Simple API object (synchronous version)
export const api = {
  get auth() { return require('./authService').authService; },
  get questions() { return require('./questionsService').questionsService; },
  get practice() { return require('./practiceService').practiceService; },
  get subjects() { return require('./subjectsService').subjectsService; },
  get analytics() { return require('./analyticsService').analyticsService; },
  get ai() { return require('./aiService').aiService; },
  get user() { return require('./userService').userService; },
}; 