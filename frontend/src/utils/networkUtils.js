import { Alert } from 'react-native';

export const handleNetworkError = (error) => {
  console.error('Network error details:', error);
  
  if (error.code === 'NETWORK_ERROR' || 
      error.message === 'Network Error' || 
      error.message?.includes('Network Error')) {
    Alert.alert(
      'Network Error',
      'Unable to connect to the server. Please check:\n\n• Your internet connection\n• Backend server is running\n• Correct IP address configuration',
      [
        { text: 'OK' },
      ]
    );
    return true;
  }
  return false;
};

export const retryRequest = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Check if it's a network error worth retrying
      if (error.code === 'NETWORK_ERROR' || 
          error.message === 'Network Error' || 
          error.message?.includes('Network Error')) {
        console.log(`Retrying request (attempt ${attempt}/${maxRetries})`);
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      } else {
        throw error; // Don't retry non-network errors
      }
    }
  }
};

export const createRetryWrapper = (apiFunction) => {
  return async (...args) => {
    try {
      return await retryRequest(() => apiFunction(...args));
    } catch (error) {
      handleNetworkError(error);
      throw error;
    }
  };
};
