// Temporary authentication bypass for development/testing
import { tokenManager } from '../api/client';

export const createTestToken = async () => {
  // Create a fake JWT token for testing (this should only be used in development)
  const header = { alg: "HS256", typ: "JWT" };
  const payload = {
    sub: "test-user-id",
    email: "test@example.com",
    is_admin: true,
    exp: Math.floor(Date.now() / 1000) + (60 * 60 * 24), // 24 hours from now
    iat: Math.floor(Date.now() / 1000)
  };

  const encodedHeader = btoa(JSON.stringify(header));
  const encodedPayload = btoa(JSON.stringify(payload));
  const fakeSignature = btoa("fake-signature");

  const fakeToken = `${encodedHeader}.${encodedPayload}.${fakeSignature}`;
  
  // Set the fake token
  await tokenManager.setToken(fakeToken);
  await tokenManager.setRefreshToken('fake-refresh-token');
  
  console.log('=== DEVELOPMENT TOKEN CREATED ===');
  console.log('This is a fake token for development only!');
  console.log('Token set:', fakeToken.substring(0, 50) + '...');
  
  return fakeToken;
};

// Auto-create test token for development
if (__DEV__) {
  setTimeout(() => {
    console.log('Creating development authentication token...');
    createTestToken();
  }, 1000);
}
