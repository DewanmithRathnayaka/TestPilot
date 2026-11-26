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

  // Project creation form state
  const [newProjectName, setNewProjectName] = useState<string>('');
  const [newProjectDesc, setNewProjectDesc] = useState<string>('');
  const [newProjectLang, setNewProjectLang] = useState<string>('Python');
  const [isCreating, setIsCreating] = useState<boolean>(false);
  const [formFeedback, setFormFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

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
        // Token invalid or expired
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
      // FastAPI OAuth2PasswordRequestForm expects URL-encoded form data
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
        body: JSON.stringify({
          username,
          email,
          password,
        }),
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
  };

  // Handle Project Creation (Protected)
  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setIsCreating(true);
    setFormFeedback(null);

    try {
      const res = await fetch(API_ENDPOINTS.PROJECTS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: newProjectName,
          description: newProjectDesc || null,
          language: newProjectLang,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail ? JSON.stringify(data.detail) : 'Failed to save project');
      }

      setFormFeedback({
        type: 'success',
        message: `Project "${data.name}" created with ID #${data.id} in SQLite!`,
      });
      setNewProjectName('');
      setNewProjectDesc('');
      fetchProjects(token);
    } catch (err: unknown) {
      setFormFeedback({ type: 'error', message: err instanceof Error ? err.message : String(err) });
    } finally {
      setIsCreating(false);
    }
  };

  // Handle Project Deletion (Protected)
  const handleDeleteProject = async (id: number, name: string) => {
    if (!token) return;
    if (!confirm(`Are you sure you want to delete your project #${id} "${name}"?`)) return;

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
    } catch (err: unknown) {
      alert(`Deletion failed: ${err instanceof Error ? err.message : err}`);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="logo-container">
          <span className="logo-icon">✈️</span>
          <div className="logo-text">
            <h1>TestPilot</h1>
            <span className="badge">Day 5 – Auth & JWT</span>
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
            Day 5: Secure user registration, password hashing (Argon2id),
            JSON Web Tokens (JWT), and multi-tenant project authorization.
          </p>
        </section>

        {/* Backend & DB Health Card */}
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
                  <strong>🟢 System Operational (FastAPI + SQLite + JWT Security)</strong>
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

              <div className="security-note">
                <small>
                  🔒 <strong>Educational Security Note:</strong> Passwords are cryptographically hashed using
                  <strong> Argon2id</strong>. Tokens are stored in browser <code>localStorage</code> for this development MVP.
                  Production systems typically use <code>HttpOnly, SameSite=Strict</code> cookies to protect against Cross-Site Scripting (XSS).
                </small>
              </div>
            </div>
          </section>
        )}

        {/* Protected Projects Management Section (Shown when logged in) */}
        {currentUser && (
          <section className="card projects-card">
            <div className="card-header">
              <div>
                <h3>My Projects (Multi-Tenant Authorized)</h3>
                <span className="sub-tag">Logged in as {currentUser.username} • User ID #{currentUser.id}</span>
              </div>
              <button onClick={() => fetchProjects(token!)} className="btn-refresh" disabled={projectsLoading}>
                {projectsLoading ? 'Loading...' : '↻ Refresh My Projects'}
              </button>
            </div>

            <div className="card-body">
              {/* Project Creation Form */}
              <form onSubmit={handleCreateProject} className="project-form">
                <h4>+ Add New Project (Owned by {currentUser.username})</h4>
                <div className="form-row">
                  <div className="form-group flex-2">
                    <label>Project Name *</label>
                    <input
                      type="text"
                      value={newProjectName}
                      onChange={(e) => setNewProjectName(e.target.value)}
                      placeholder="e.g. Data Structures Test Suite"
                      required
                      minLength={2}
                    />
                  </div>
                  <div className="form-group flex-1">
                    <label>Language</label>
                    <select
                      value={newProjectLang}
                      onChange={(e) => setNewProjectLang(e.target.value)}
                    >
                      <option value="Python">Python</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Description (Optional)</label>
                  <textarea
                    value={newProjectDesc}
                    onChange={(e) => setNewProjectDesc(e.target.value)}
                    placeholder="Short description of the project"
                    rows={2}
                  />
                </div>

                <button type="submit" className="btn-submit" disabled={isCreating}>
                  {isCreating ? 'Saving to SQLite...' : '+ Add Project to Database'}
                </button>

                {formFeedback && (
                  <div className={`form-feedback ${formFeedback.type}`}>
                    {formFeedback.message}
                  </div>
                )}
              </form>

              <hr className="divider" />

              <h4>Your Stored Projects ({projects.length})</h4>

              {projectsLoading && (
                <div className="empty-state">
                  <span className="dot pulse"></span> Loading projects for {currentUser.username}...
                </div>
              )}

              {projectsError && (
                <div className="status-badge error">
                  <strong>Error loading projects:</strong> {projectsError}
                </div>
              )}

              {!projectsLoading && !projectsError && projects.length === 0 && (
                <div className="empty-state">
                  <p>📂 You have not uploaded any projects yet.</p>
                  <p className="subtext">Use the form above to add a project owned by your account.</p>
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
                        <span className={`status-pill status-${proj.status.toLowerCase()}`}>
                          {proj.status}
                        </span>
                      </div>

                      <p className="project-desc">
                        {proj.description || <em>No description provided</em>}
                      </p>

                      <div className="project-card-footer">
                        <div className="meta-info">
                          <span className="lang-tag">🐍 {proj.language}</span>
                          <span className="date-tag">
                            {new Date(proj.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <button
                          onClick={() => handleDeleteProject(proj.id, proj.name)}
                          className="btn-delete"
                          title="Delete project from SQLite"
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>TestPilot – University Software Testing Platform • Day 5 Authentication Complete</p>
      </footer>
    </div>
  );
}
