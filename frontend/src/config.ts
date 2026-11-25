/**
 * TestPilot Frontend Configuration
 * Manages API endpoint URLs and global client settings.
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/health`,
  INFO: `${API_BASE_URL}/api/info`,
  ROOT: `${API_BASE_URL}/api/`,
  GREETING: `${API_BASE_URL}/api/greeting`,
  TEST_MESSAGE: `${API_BASE_URL}/api/test-message`,
};
