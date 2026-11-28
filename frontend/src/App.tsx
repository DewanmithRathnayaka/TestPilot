import React, { useState, useEffect } from 'react';
import { API_BASE_URL, API_ENDPOINTS } from './config';

interface HealthData {
  status: string;
  application: string;
  message: string;
}

interface InfoData {
  name: string;
  description: string;
  version: string;
  status: string;
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

interface Project {
  id: number;
  name: string;
  description: string | null;
  language: string;
  status: string;
  created_at: string;
  user_id?: number;
  original_filename?: string | null;
  source_file_count: number;
  test_file_count: number;
  validation_status: string;
}

interface SyntaxErrorDetail {
  file: string;
  line: number | null;
  column: number | null;
  message: string;
}

interface ProjectAnalysisResponse {
  project_id: number;
  project_name: string;
  language: string;
  test_framework: string;
  analysis_status: string;
  structure_valid: boolean;
  source_file_count: number;
  test_file_count: number;
  python_file_count: number;
  total_file_count: number;
  total_project_size: number;
  test_function_count: number;
  test_class_count: number;
  test_method_count: number;
  syntax_error_count: number;
  syntax_errors: SyntaxErrorDetail[];
  dependencies: string[];
  has_pytest: boolean;
  has_requirements_file: boolean;
  has_readme: boolean;
  warnings: string[];
  analysis_timestamp: string;
}

export default function App() {
  // System status state
  const [health, setHealth] = useState<HealthData | null>(null);
  const [info, setInfo] = useState<InfoData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Authentication State
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('testpilot_token'));
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [authTab, setAuthTab] = useState<'login' | 'register'>('login');
  const [authLoading, setAuthLoading] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authSuccess, setAuthSuccess] = useState<string | null>(null);

  // Auth form inputs
  const [username, setUsername] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  // Projects state (Protected)
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState<boolean>(false);
  const [projectsError, setProjectsError] = useState<string | null>(null);

  // Day 6 ZIP Upload State
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState<boolean>(false);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Day 7 Static Analysis State
  const [analyzingProjectId, setAnalyzingProjectId] = useState<number | null>(null);
  const [analysisResults, setAnalysisResults] = useState<Record<number, ProjectAnalysisResponse>>({});
  const [analysisErrors, setAnalysisErrors] = useState<Record<number, string>>({});
  const [activeAnalysisModal, setActiveAnalysisModal] = useState<ProjectAnalysisResponse | null>(null);

  // Check backend health
  const checkBackendStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const [resHealth, resInfo] = await Promise.all([
        fetch(API_ENDPOINTS.HEALTH),
        fetch(API_ENDPOINTS.INFO),
      ]);

      if (!resHealth.ok) throw new Error(`Health HTTP ${resHealth.status}`);
      if (!resInfo.ok) throw new Error(`Info HTTP ${resInfo.status}`);

      const healthJson = await resHealth.json();
      const infoJson = await resInfo.json();

      setHealth(healthJson);
      setInfo(infoJson);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Network error';
      setError(`Cannot reach backend at ${API_BASE_URL}: ${msg}`);
      setHealth(null);
      setInfo(null);
    } finally {
      setLoading(false);
    }
  };

  // Fetch current user profile with token
  const fetchUserProfile = async (authToken: string) => {
    try {
      const res = await fetch(API_ENDPOINTS.AUTH_ME, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (res.ok) {
        const user: UserProfile = await res.json();
        setCurrentUser(user);
        fetchProjects(authToken);
      } else {
        handleLogout();
      }
    } catch {
      handleLogout();
    }
  };

  // Fetch user-owned projects from backend
  const fetchProjects = async (authToken: string) => {
    setProjectsLoading(true);
    setProjectsError(null);
    try {
      const res = await fetch(API_ENDPOINTS.PROJECTS, {
        headers: { Authorization: `Bearer ${authToken}` },
      });
      if (!res.ok) throw new Error(`Failed to fetch projects (HTTP ${res.status})`);
      const data: Project[] = await res.json();
      setProjects(data);
    } catch (err: unknown) {
      setProjectsError(err instanceof Error ? err.message : 'Unknown database error');
    } finally {
      setProjectsLoading(false);
    }
  };

  useEffect(() => {
    checkBackendStatus();
    if (token) {
      fetchUserProfile(token);
    }
  }, [token]);

  // Handle Login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthSuccess(null);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch(API_ENDPOINTS.AUTH_LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Login failed. Please check your credentials.');
      }

      const receivedToken = data.access_token;
      localStorage.setItem('testpilot_token', receivedToken);
      setToken(receivedToken);
      setPassword('');
      setAuthSuccess('Login successful! Redirecting to dashboard...');
    } catch (err: unknown) {
      setAuthError(err instanceof Error ? err.message : String(err));
    } finally {
      setAuthLoading(false);
    }
  };

  // Handle Registration
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError(null);
    setAuthSuccess(null);

    try {
      const res = await fetch(API_ENDPOINTS.AUTH_REGISTER, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await res.json();
      if (!res.ok) {
        const errorDetail = typeof data.detail === 'string'
          ? data.detail
          : JSON.stringify(data.detail);
        throw new Error(errorDetail || 'Registration failed.');
      }

      setAuthSuccess(`Account "${data.username}" created successfully! Please log in.`);
      setAuthTab('login');
      setPassword('');
    } catch (err: unknown) {
      setAuthError(err instanceof Error ? err.message : String(err));
    } finally {
      setAuthLoading(false);
    }
  };

  // Handle Logout
  const handleLogout = () => {
    localStorage.removeItem('testpilot_token');
    setToken(null);
    setCurrentUser(null);
    setProjects([]);
    setAuthSuccess(null);
    setAuthError(null);
    setSelectedFile(null);
    setUploadSuccess(null);
    setUploadError(null);
  };

  // Handle ZIP File Selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setUploadError(null);
      setUploadSuccess(null);
    }
  };

  // Handle Day 6 ZIP Project Upload
  const handleUploadProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !token) return;

    setUploadLoading(true);
    setUploadError(null);
    setUploadSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await fetch(API_ENDPOINTS.PROJECTS_UPLOAD, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          // Notice: Content-Type is omitted so browser sets multipart boundary automatically
        },
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Upload failed.');
      }

      setUploadSuccess(
        `✓ Project "${data.name}" uploaded successfully! Validated: ${data.source_file_count} Python files, ${data.test_file_count} Pytest test files.`
      );
      setSelectedFile(null);
      // Reset the file input element
      const fileInput = document.getElementById('project-zip-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      fetchProjects(token);
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploadLoading(false);
    }
  };

  // Handle Project Deletion (Protected)
  const handleDeleteProject = async (id: number, name: string) => {
    if (!token) return;
    if (!confirm(`Are you sure you want to delete project #${id} "${name}"?`)) return;

    try {
      const res = await fetch(`${API_ENDPOINTS.PROJECTS}/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || `HTTP ${res.status}`);
      }
      setProjects((prev) => prev.filter((p) => p.id !== id));
      setAnalysisResults((prev) => {
        const copy = { ...prev };
        delete copy[id];
        return copy;
      });
    } catch (err: unknown) {
      alert(`Deletion failed: ${err instanceof Error ? err.message : err}`);
    }
  };

  // Handle Project Static Analysis (Day 7)
  const handleAnalyzeProject = async (projectId: number) => {
    if (!token) return;
    setAnalyzingProjectId(projectId);
    setAnalysisErrors((prev) => ({ ...prev, [projectId]: '' }));

    try {
      const res = await fetch(API_ENDPOINTS.PROJECT_ANALYZE(projectId), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || `Analysis failed with HTTP ${res.status}`);
      }

      setAnalysisResults((prev) => ({ ...prev, [projectId]: data }));
      setActiveAnalysisModal(data);
      // Refresh project list so status and file counts sync with DB
      fetchProjects(token);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setAnalysisErrors((prev) => ({ ...prev, [projectId]: msg }));
    } finally {
      setAnalyzingProjectId(null);
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="logo-container">
          <span className="logo-icon">✈️</span>
          <div className="logo-text">
            <h1>TestPilot</h1>
            <span className="badge">Day 7 – Static Structure & AST Analysis</span>
          </div>
        </div>

        <div className="header-status">
          {currentUser ? (
            <div className="user-profile-badge">
              <span className="user-avatar">👤</span>
              <div className="user-info">
                <strong>{currentUser.username}</strong>
                <span className="user-email">{currentUser.email}</span>
              </div>
              <button onClick={handleLogout} className="btn-logout" title="Log out">
                Sign Out
              </button>
            </div>
          ) : (
            <span className="guest-badge">🔒 Guest (Not logged in)</span>
          )}
          <a
            href={`${API_BASE_URL}/docs`}
            target="_blank"
            rel="noreferrer"
            className="swagger-link"
          >
            Swagger Docs ↗
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <section className="hero">
          <h2>Automated Software Testing Platform</h2>
          <p className="hero-subtitle">
            Day 6: Secure project upload pipeline. Protects against Zip Slip,
            decompression bombs, symlinks, and enforces standard Pytest project layouts.
          </p>
        </section>

        {/* Backend Status Card */}
        <section className="card status-card">
          <div className="card-header">
            <h3>System Status</h3>
            <button onClick={checkBackendStatus} className="btn-refresh" disabled={loading}>
              {loading ? 'Checking...' : '↻ Re-check'}
            </button>
          </div>
          <div className="card-body">
            {loading && <div className="status-badge loading"><span className="dot pulse"></span> Checking backend status...</div>}
            {error && <div className="status-badge error"><strong>Backend Offline:</strong> {error}</div>}
            {health && info && !loading && (
              <div className="status-badge success">
                <div className="badge-row">
                  <span className="dot success-dot"></span>
                  <strong>🟢 System Operational (FastAPI + SQLite + Secure Uploads)</strong>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Authentication Card (Shown when NOT logged in) */}
        {!currentUser && (
          <section className="card auth-card">
            <div className="card-header">
              <div className="auth-tabs">
                <button
                  className={`tab-btn ${authTab === 'login' ? 'active' : ''}`}
                  onClick={() => { setAuthTab('login'); setAuthError(null); }}
                >
                  Sign In
                </button>
                <button
                  className={`tab-btn ${authTab === 'register' ? 'active' : ''}`}
                  onClick={() => { setAuthTab('register'); setAuthError(null); }}
                >
                  Create Account
                </button>
              </div>
              <span className="sub-tag">Argon2id + JWT Bearer</span>
            </div>

            <div className="card-body">
              {authError && <div className="status-badge error"><strong>Error:</strong> {authError}</div>}
              {authSuccess && <div className="status-badge success"><strong>Success:</strong> {authSuccess}</div>}

              {authTab === 'login' ? (
                <form onSubmit={handleLogin} className="auth-form">
                  <div className="form-group">
                    <label>Username or Email</label>
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="e.g. alice_dev or alice@university.edu"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter your password"
                      required
                    />
                  </div>
                  <button type="submit" className="btn-submit" disabled={authLoading}>
                    {authLoading ? 'Signing In...' : 'Sign In with JWT'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleRegister} className="auth-form">
                  <div className="form-group">
                    <label>Username (3-50 alphanumeric)</label>
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="e.g. alice_dev"
                      required
                      minLength={3}
                    />
                  </div>
                  <div className="form-group">
                    <label>Email Address</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="e.g. alice@university.edu"
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Password (min 6 chars)</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Create a strong password"
                      required
                      minLength={6}
                    />
                  </div>
                  <button type="submit" className="btn-submit" disabled={authLoading}>
                    {authLoading ? 'Registering...' : 'Register New Account'}
                  </button>
                </form>
              )}
            </div>
          </section>
        )}

        {/* Protected Project Upload & Management (Shown when logged in) */}
        {currentUser && (
          <>
            {/* Day 6: ZIP Upload Box */}
            <section className="card upload-card">
              <div className="card-header">
                <div>
                  <h3>Upload Python Project (.ZIP)</h3>
                  <span className="sub-tag">Max 10 MB • Standard Pytest Layout</span>
                </div>
              </div>

              <div className="card-body">
                <div className="layout-guide">
                  <strong>Expected Project Layout:</strong>
                  <code>
                    project_name.zip &gt; src/ (*.py) + tests/ (test_*.py) + requirements.txt
                  </code>
                </div>

                <form onSubmit={handleUploadProject} className="upload-form">
                  <div className="file-drop-area">
                    <input
                      type="file"
                      id="project-zip-input"
                      accept=".zip,application/zip"
                      onChange={handleFileChange}
                      className="file-input"
                    />
                    <label htmlFor="project-zip-input" className="file-label">
                      <span className="upload-icon">📦</span>
                      <span className="file-prompt">
                        {selectedFile ? selectedFile.name : 'Click to select project .ZIP archive'}
                      </span>
                      {selectedFile && (
                        <span className="file-size-badge">
                          {formatFileSize(selectedFile.size)}
                        </span>
                      )}
                    </label>
                  </div>

                  <button
                    type="submit"
                    className="btn-submit btn-upload"
                    disabled={!selectedFile || uploadLoading}
                  >
                    {uploadLoading ? 'Inspecting & Extracting Safely...' : '🚀 Upload & Validate Project'}
                  </button>
                </form>

                {uploadSuccess && (
                  <div className="status-badge success">
                    <strong>Upload Succeeded:</strong> {uploadSuccess}
                  </div>
                )}

                {uploadError && (
                  <div className="status-badge error">
                    <strong>Validation Rejected:</strong> {uploadError}
                  </div>
                )}
              </div>
            </section>

            {/* Projects List Card */}
            <section className="card projects-card">
              <div className="card-header">
                <div>
                  <h3>My Projects ({projects.length})</h3>
                  <span className="sub-tag">Authenticated as {currentUser.username}</span>
                </div>
                <button onClick={() => fetchProjects(token!)} className="btn-refresh" disabled={projectsLoading}>
                  {projectsLoading ? 'Loading...' : '↻ Refresh Projects'}
                </button>
              </div>

              <div className="card-body">
                {projectsLoading && (
                  <div className="empty-state">
                    <span className="dot pulse"></span> Loading projects for {currentUser.username}...
                  </div>
                )}

                {projectsError && (
                  <div className="status-badge error">
                    <strong>Error:</strong> {projectsError}
                  </div>
                )}

                {!projectsLoading && !projectsError && projects.length === 0 && (
                  <div className="empty-state">
                    <p>📂 No projects uploaded yet.</p>
                    <p className="subtext">Upload your first Python project ZIP archive above.</p>
                  </div>
                )}

                {!projectsLoading && !projectsError && projects.length > 0 && (
                  <div className="projects-grid">
                    {projects.map((proj) => (
                      <div key={proj.id} className="project-card">
                        <div className="project-card-header">
                          <div>
                            <span className="project-id-tag">Project #{proj.id}</span>
                            <h5 className="project-title">{proj.name}</h5>
                          </div>
                          <span className={`status-pill status-${proj.validation_status.toLowerCase()}`}>
                            {proj.validation_status}
                          </span>
                        </div>

                        <p className="project-desc">
                          {proj.description || <em>No description provided</em>}
                        </p>

                        <div className="project-stats-grid">
                          <div className="stat-pill">
                            <span className="stat-label">Source Files</span>
                            <span className="stat-val">📄 {proj.source_file_count}</span>
                          </div>
                          <div className="stat-pill">
                            <span className="stat-label">Test Files</span>
                            <span className="stat-val">🧪 {proj.test_file_count}</span>
                          </div>
                        </div>

                        {/* Day 7 Static Analysis Preview if available */}
                        {analysisResults[proj.id] && (
                          <div className="analysis-summary-pill">
                            <span>🔍 AST Tests: {analysisResults[proj.id].test_function_count + analysisResults[proj.id].test_method_count}</span>
                            <span>•</span>
                            <span className={analysisResults[proj.id].syntax_error_count > 0 ? 'text-danger' : 'text-success'}>
                              {analysisResults[proj.id].syntax_error_count > 0
                                ? `⚠️ ${analysisResults[proj.id].syntax_error_count} syntax err`
                                : '✓ Syntax Clean'}
                            </span>
                          </div>
                        )}

                        {analysisErrors[proj.id] && (
                          <div className="status-badge error" style={{ margin: '0.4rem 0', padding: '4px 8px', fontSize: '0.75rem' }}>
                            {analysisErrors[proj.id]}
                          </div>
                        )}

                        <div className="project-card-footer">
                          <div className="meta-info">
                            <span className="lang-tag">🐍 {proj.language}</span>
                            <span className="date-tag">
                              {new Date(proj.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <div className="card-actions">
                            <button
                              onClick={() => handleAnalyzeProject(proj.id)}
                              className="btn-analyze"
                              disabled={analyzingProjectId === proj.id}
                              title="Perform static AST inspection, detect syntax errors and discover Pytest test candidates"
                            >
                              {analyzingProjectId === proj.id ? '⚡ Analyzing...' : '🔍 Analyze AST'}
                            </button>
                            {analysisResults[proj.id] && (
                              <button
                                onClick={() => setActiveAnalysisModal(analysisResults[proj.id])}
                                className="btn-view-report"
                                title="View static AST analysis report"
                              >
                                📊 Report
                              </button>
                            )}
                            <button
                              onClick={() => handleDeleteProject(proj.id, proj.name)}
                              className="btn-delete"
                              title="Delete project"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>

            {/* Day 7: Static Analysis Report Modal */}
            {activeAnalysisModal && (
              <div className="modal-backdrop" onClick={() => setActiveAnalysisModal(null)}>
                <div className="modal-card" onClick={(e) => e.stopPropagation()}>
                  <div className="modal-header">
                    <div>
                      <span className="project-id-tag">Project #{activeAnalysisModal.project_id}</span>
                      <h3>Static Analysis Report: {activeAnalysisModal.project_name}</h3>
                      <span className="sub-tag">Pure Static AST Inspection (Zero Dynamic Execution)</span>
                    </div>
                    <button className="btn-close" onClick={() => setActiveAnalysisModal(null)}>✕</button>
                  </div>

                  <div className="modal-body">
                    {/* Structure & Validity Status */}
                    <div className="analysis-status-banner">
                      <div>
                        <strong>Structure Verification:</strong>{' '}
                        <span className={`status-pill status-${activeAnalysisModal.structure_valid ? 'valid' : 'invalid'}`}>
                          {activeAnalysisModal.structure_valid ? 'Structure Valid' : 'Structure Issues Detected'}
                        </span>
                      </div>
                      <span className="sub-tag">
                        Analyzed at {new Date(activeAnalysisModal.analysis_timestamp).toLocaleTimeString()}
                      </span>
                    </div>

                    {/* Discovery Metrics Grid */}
                    <div className="modal-metrics-grid">
                      <div className="metric-box">
                        <span className="metric-label">Source Files (src/)</span>
                        <span className="metric-value">📄 {activeAnalysisModal.source_file_count}</span>
                      </div>
                      <div className="metric-box">
                        <span className="metric-label">Pytest Files (tests/)</span>
                        <span className="metric-value">🧪 {activeAnalysisModal.test_file_count}</span>
                      </div>
                      <div className="metric-box">
                        <span className="metric-label">Total Python Files</span>
                        <span className="metric-value">🐍 {activeAnalysisModal.python_file_count}</span>
                      </div>
                      <div className="metric-box">
                        <span className="metric-label">Project Size</span>
                        <span className="metric-value">💾 {formatFileSize(activeAnalysisModal.total_project_size)}</span>
                      </div>
                    </div>

                    {/* AST Pytest Candidate Discovery */}
                    <div className="report-section">
                      <h4>🧪 Pytest Candidate Discovery (AST Inferred)</h4>
                      <div className="modal-metrics-grid">
                        <div className="metric-box">
                          <span className="metric-label">Test Functions (test_*)</span>
                          <span className="metric-value">{activeAnalysisModal.test_function_count}</span>
                        </div>
                        <div className="metric-box">
                          <span className="metric-label">Test Classes (Test*)</span>
                          <span className="metric-value">{activeAnalysisModal.test_class_count}</span>
                        </div>
                        <div className="metric-box">
                          <span className="metric-label">Class Methods (test_*)</span>
                          <span className="metric-value">{activeAnalysisModal.test_method_count}</span>
                        </div>
                        <div className="metric-box highlight">
                          <span className="metric-label">Total Candidate Tests</span>
                          <span className="metric-value">
                            {activeAnalysisModal.test_function_count + activeAnalysisModal.test_method_count}
                          </span>
                        </div>
                      </div>
                      <p className="discovery-note">
                        ℹ️ <em>Note: Candidates are top-level and class-level test definitions identified statically via AST without importing modules or running code.</em>
                      </p>
                    </div>

                    {/* Dependencies and Requirements */}
                    <div className="report-section">
                      <h4>📦 Environment & Requirements Check</h4>
                      <div className="requirements-summary">
                        <span><strong>requirements.txt:</strong> {activeAnalysisModal.has_requirements_file ? '✅ Found' : '❌ Not Found'}</span>
                        <span><strong>Pytest Declared:</strong> {activeAnalysisModal.has_pytest ? '✅ Yes' : '⚠️ Missing'}</span>
                        <span><strong>README:</strong> {activeAnalysisModal.has_readme ? '✅ Found' : 'ℹ️ None'}</span>
                      </div>
                      {activeAnalysisModal.dependencies.length > 0 && (
                        <div className="dep-tags-list">
                          {activeAnalysisModal.dependencies.map((dep, idx) => (
                            <span key={idx} className="dep-pill">{dep}</span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Static Syntax Validation Section */}
                    <div className="report-section">
                      <h4>🔍 AST Syntax Validation</h4>
                      {activeAnalysisModal.syntax_error_count === 0 ? (
                        <div className="status-badge success">
                          ✓ All {activeAnalysisModal.python_file_count} Python file(s) parsed cleanly with zero syntax errors.
                        </div>
                      ) : (
                        <div className="syntax-errors-container">
                          <div className="status-badge error">
                            ⚠️ Found {activeAnalysisModal.syntax_error_count} file(s) with syntax errors:
                          </div>
                          <ul className="syntax-error-list">
                            {activeAnalysisModal.syntax_errors.map((err, idx) => (
                              <li key={idx} className="syntax-error-item">
                                <strong>{err.file}</strong> (Line {err.line ?? '?'}, Col {err.column ?? '?'}):
                                <span> {err.message}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>

                    {/* Advisory Warnings */}
                    {activeAnalysisModal.warnings.length > 0 && (
                      <div className="report-section">
                        <h4>⚠️ Diagnostic Advisory Warnings</h4>
                        <ul className="warnings-list">
                          {activeAnalysisModal.warnings.map((warn, idx) => (
                            <li key={idx} className="warning-item">{warn}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  <div className="modal-footer">
                    <button className="btn-submit" onClick={() => setActiveAnalysisModal(null)}>
                      Close Report
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>TestPilot – University Software Testing Platform • Day 7 AST Static Analysis & Test Discovery Complete</p>
      </footer>
    </div>
  );
}
