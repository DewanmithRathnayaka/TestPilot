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

interface Project {
  id: number;
  name: string;
  description: string | null;
  language: string;
  status: string;
  created_at: string;
}

export default function App() {
  // System status state
  const [health, setHealth] = useState<HealthData | null>(null);
  const [info, setInfo] = useState<InfoData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Projects state (Day 4 Database CRUD)
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState<boolean>(true);
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

  // Fetch real projects from SQLite database
  const fetchProjects = async () => {
    setProjectsLoading(true);
    setProjectsError(null);
    try {
      const res = await fetch(API_ENDPOINTS.PROJECTS);
      if (!res.ok) {
        throw new Error(`Failed to fetch projects (HTTP ${res.status})`);
      }
      const data: Project[] = await res.json();
      setProjects(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown database error';
      setProjectsError(msg);
    } finally {
      setProjectsLoading(false);
    }
  };

  useEffect(() => {
    checkBackendStatus();
    fetchProjects();
  }, []);

  // Handle project creation
  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsCreating(true);
    setFormFeedback(null);

    try {
      const res = await fetch(API_ENDPOINTS.PROJECTS, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
      fetchProjects(); // Refresh database list
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setFormFeedback({ type: 'error', message: msg });
    } finally {
      setIsCreating(false);
    }
  };

  // Handle project deletion
  const handleDeleteProject = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete project #${id} "${name}" from SQLite?`)) {
      return;
    }

    try {
      const res = await fetch(`${API_ENDPOINTS.PROJECTS}/${id}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      // Remove from state immediately
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err: unknown) {
      alert(`Failed to delete project: ${err instanceof Error ? err.message : err}`);
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
            <span className="badge">Day 4 – SQLite & SQLAlchemy</span>
          </div>
        </div>
        <div className="header-status">
          <span className="api-url-tag">API: {API_BASE_URL}</span>
          <a
            href={`${API_BASE_URL}/docs`}
            target="_blank"
            rel="noreferrer"
            className="swagger-link"
          >
            Open Swagger Docs ↗
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <section className="hero">
          <h2>Automated Software Testing Platform</h2>
          <p className="hero-subtitle">
            Day 4: Relational persistence layer active. Records are saved directly
            to SQLite database (<code>testpilot.db</code>) via SQLAlchemy ORM.
          </p>
        </section>

        {/* Backend Status Card */}
        <section className="card status-card">
          <div className="card-header">
            <h3>Backend & Database Connection</h3>
            <button onClick={checkBackendStatus} className="btn-refresh" disabled={loading}>
              {loading ? 'Checking...' : '↻ Re-check'}
            </button>
          </div>
          <div className="card-body">
            {loading && (
              <div className="status-badge loading">
                <span className="dot pulse"></span>
                Connecting to FastAPI backend...
              </div>
            )}
            {error && (
              <div className="status-badge error">
                <span className="dot error-dot"></span>
                <strong>Disconnected:</strong> {error}
                <p className="help-text">
                  Start backend with: <code>uvicorn app.main:app --reload</code>
                </p>
              </div>
            )}
            {health && info && !loading && (
              <div className="status-badge success">
                <div className="badge-row">
                  <span className="dot success-dot"></span>
                  <strong>🟢 Backend Operational & SQLite Connected</strong>
                </div>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Application:</span>
                    <span className="value">{info.name}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Version:</span>
                    <span className="value">{info.version}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Database:</span>
                    <span className="value">SQLite 3 (testpilot.db)</span>
                  </div>
                  <div className="info-item">
                    <span className="label">ORM:</span>
                    <span className="value">SQLAlchemy 2.1</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Day 4: Projects Management Section */}
        <section className="card projects-card">
          <div className="card-header">
            <div>
              <h3>Stored Projects</h3>
              <span className="sub-tag">Retrieved live via GET /api/projects</span>
            </div>
            <button onClick={fetchProjects} className="btn-refresh" disabled={projectsLoading}>
              {projectsLoading ? 'Loading...' : '↻ Refresh List'}
            </button>
          </div>

          <div className="card-body">
            {/* Project Creation Form */}
            <form onSubmit={handleCreateProject} className="project-form">
              <h4>Create New Project Record (POST /api/projects)</h4>
              <div className="form-row">
                <div className="form-group flex-2">
                  <label>Project Name *</label>
                  <input
                    type="text"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="e.g. My Pytest Project"
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

            {/* Project List Display */}
            <h4>Projects in Database ({projects.length})</h4>

            {projectsLoading && (
              <div className="empty-state">
                <span className="dot pulse"></span> Loading projects from SQLite...
              </div>
            )}

            {projectsError && (
              <div className="status-badge error">
                <strong>Error loading projects:</strong> {projectsError}
              </div>
            )}

            {!projectsLoading && !projectsError && projects.length === 0 && (
              <div className="empty-state">
                <p>📂 No projects stored in SQLite yet.</p>
                <p className="subtext">Use the form above to add your first project record.</p>
              </div>
            )}

            {!projectsLoading && !projectsError && projects.length > 0 && (
              <div className="projects-grid">
                {projects.map((proj) => (
                  <div key={proj.id} className="project-card">
                    <div className="project-card-header">
                      <div>
                        <span className="project-id-tag">#{proj.id}</span>
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
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>TestPilot – University Software Testing Platform • Day 4 SQLite Complete</p>
      </footer>
    </div>
  );
}
