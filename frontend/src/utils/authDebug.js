import { tokenManager } from '../api/client';
import { authService } from '../api/authService';

export const authDebug = {
  async checkCurrentAuth() {
    try {
      const token = await tokenManager.getToken();
      const refreshToken = await tokenManager.getRefreshToken();
      
      console.log('=== AUTH DEBUG ===');
      console.log('Current token:', token ? 'Present' : 'Missing');
      console.log('Refresh token:', refreshToken ? 'Present' : 'Missing');
      
      if (token) {
        // Try to decode token to see expiry (basic check)
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          const now = Math.floor(Date.now() / 1000);
          console.log('Token expires at:', new Date(payload.exp * 1000));
          console.log('Token is expired:', payload.exp < now);
        } catch (e) {
          console.log('Could not decode token');
        }
      }
      
      return { token, refreshToken };
    } catch (error) {
      console.error('Auth debug error:', error);
      return null;
    }
  },

  async testLogin() {
    try {
      console.log('=== TESTING LOGIN ===');
      // Use test credentials - you should replace these with real ones
      const credentials = {
        email: 'admin@example.com',
        password: 'admin123'
      };
      
      console.log('Attempting login with:', credentials.email);
      const result = await authService.login(credentials);
      console.log('Login successful:', result);
      
      return result;
    } catch (error) {
      console.error('Test login failed:', error);
      
      // Try with different endpoint format
      try {
        console.log('Trying token endpoint...');
        const result = await authService.getToken({
          username: 'admin@example.com',
          password: 'admin123'
        });
        console.log('Token endpoint successful:', result);
        return result;
      } catch (tokenError) {
        console.error('Token endpoint also failed:', tokenError);
        return null;
      }
    }
  }
};

// Auto-run debug check
setTimeout(() => {
  authDebug.checkCurrentAuth();
}, 2000);
