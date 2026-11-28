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
  PROJECTS: `${API_BASE_URL}/api/projects`,
  PROJECTS_UPLOAD: `${API_BASE_URL}/api/projects/upload`,
  PROJECT_ANALYZE: (id: number) => `${API_BASE_URL}/api/projects/${id}/analyze`,
  AUTH_REGISTER: `${API_BASE_URL}/api/auth/register`,
  AUTH_LOGIN: `${API_BASE_URL}/api/auth/login`,
  AUTH_ME: `${API_BASE_URL}/api/auth/me`,
};
