import Constants from 'expo-constants';

// Get the local IP address for development
const getLocalIP = () => {
  if (__DEV__) {
    // For Expo development, we can use the manifest to get the debuggerHost
    const debuggerHost = Constants.manifest?.debuggerHost?.split(':')[0];
    if (debuggerHost) {
      return debuggerHost;
    }
    // Fallback to common development IPs
    return '172.16.0.59'; // Current machine IP
  }
  // For production, use your actual domain
  return 'your-production-domain.com';
};

const getAPIBaseURL = () => {
  if (__DEV__) {
    const localIP = getLocalIP();
    return `http://${localIP}:8000/api/v1`;
  }
  // Production URL
  return 'https://your-production-domain.com/api/v1';
};

export const API_CONFIG = {
  BASE_URL: getAPIBaseURL(),
  TIMEOUT: 30000, // Increased timeout for mobile networks
  RETRY_ATTEMPTS: 3,
};

export default API_CONFIG;
