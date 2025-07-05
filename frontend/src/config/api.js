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
    return '172.20.230.253'; // Current machine IP
  }
  // For production, use your actual domain
  return 'your-production-domain.com';
};

const getAPIBaseURL = () => {
  if (__DEV__) {
    // Use ngrok URL for development to avoid network connectivity issues
    return 'https://9dc8-125-17-13-54.ngrok-free.app/api/v1';
    
    // Alternative: Use local IP if ngrok is not available
    // const localIP = getLocalIP();
    // return `http://${localIP}:8000/api/v1`;
  }
  // Production URL
  return 'https://your-production-domain.com/api/v1';
};

export const API_CONFIG = {
  BASE_URL: getAPIBaseURL(),
  TIMEOUT: 30000, // Increased timeout for mobile networks
  RETRY_ATTEMPTS: 3,
};

// Debug logging for development
if (__DEV__) {
  console.log('=== API CONFIGURATION ===');
  console.log('BASE_URL:', API_CONFIG.BASE_URL);
  console.log('Network IP detected:', getLocalIP());
  console.log('========================');
}

export default API_CONFIG;
