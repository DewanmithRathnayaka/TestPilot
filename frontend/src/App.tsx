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

interface TestMessageResponse {
  success: boolean;
  confirmation: string;
  echo: {
    username: string;
    message: string;
  };
}

export default function App() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [info, setInfo] = useState<InfoData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Interactive POST test state
  const [username, setUsername] = useState<string>('Student Tester');
  const [testMsg, setTestMsg] = useState<string>('Hello from TestPilot React Frontend!');
  const [postResponse, setPostResponse] = useState<TestMessageResponse | null>(null);
  const [postError, setPostError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  // Fetch backend status on mount
  const checkBackendStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const [resHealth, resInfo] = await Promise.all([
        fetch(API_ENDPOINTS.HEALTH),
        fetch(API_ENDPOINTS.INFO),
      ]);

      if (!resHealth.ok) {
        throw new Error(`Health check returned HTTP status ${resHealth.status}`);
      }
      if (!resInfo.ok) {
        throw new Error(`Info check returned HTTP status ${resInfo.status}`);
      }

      const healthJson = await resHealth.json();
      const infoJson = await resInfo.json();

      setHealth(healthJson);
      setInfo(infoJson);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown network error';
      setError(`Cannot connect to TestPilot backend at ${API_BASE_URL}: ${errorMessage}`);
      setHealth(null);
      setInfo(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkBackendStatus();
  }, []);

  // Handle interactive POST testing
  const handleSendTestMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setPostError(null);
    setPostResponse(null);

    try {
      const res = await fetch(API_ENDPOINTS.TEST_MESSAGE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          message: testMsg,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        // FastAPI returns 422 with { detail: [...] } for validation errors
        throw new Error(JSON.stringify(data.detail || data, null, 2));
      }

      setPostResponse(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      setPostError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <header className="header">
        <div className="logo-container">
          <span className="logo-icon">✈️</span>
          <div className="logo-text">
            <h1>TestPilot</h1>
            <span className="badge">Day 3 Setup</span>
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

      {/* Hero Section */}
      <main className="main-content">
        <section className="hero">
          <h2>Automated Software Testing Platform</h2>
          <p className="hero-subtitle">
            Welcome to Day 3 of development! This platform bridges React, FastAPI,
            and isolated Docker sandboxes for university code evaluation.
          </p>
        </section>

        {/* Backend Connection Status Card */}
        <section className="card status-card">
          <div className="card-header">
            <h3>Backend Connectivity Status</h3>
            <button onClick={checkBackendStatus} className="btn-refresh" disabled={loading}>
              {loading ? 'Checking...' : '↻ Re-check'}
            </button>
          </div>

          <div className="card-body">
            {loading && (
              <div className="status-badge loading">
                <span className="dot pulse"></span>
                Connecting to FastAPI backend at {API_BASE_URL}...
              </div>
            )}

            {error && (
              <div className="status-badge error">
                <span className="dot error-dot"></span>
                <strong>Connection Error:</strong> {error}
                <p className="help-text">
                  Make sure the backend is running with: <code>uvicorn app.main:app --reload</code>
                </p>
              </div>
            )}

            {health && info && !loading && (
              <div className="status-badge success">
                <div className="badge-row">
                  <span className="dot success-dot"></span>
                  <strong>🟢 Backend Connected & Operational</strong>
                </div>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Application:</span>
                    <span className="value">{info.name}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">API Version:</span>
                    <span className="value">{info.version}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Health Status:</span>
                    <span className="value">{health.status}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Server Message:</span>
                    <span className="value">{health.message}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Interactive REST API Verification Panel */}
        <section className="card api-test-card">
          <div className="card-header">
            <h3>Interactive API Test (POST /api/test-message)</h3>
            <span className="sub-tag">Pydantic Validation Demonstration</span>
          </div>

          <div className="card-body">
            <p className="instruction">
              Test how FastAPI receives JSON payloads and how Pydantic enforces validation rules
              (Username: 2–50 chars, Message: 3–500 chars).
            </p>

            <form onSubmit={handleSendTestMessage} className="test-form">
              <div className="form-group">
                <label>Username (min 2 chars):</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter username"
                  required
                />
              </div>

              <div className="form-group">
                <label>Test Message (min 3 chars):</label>
                <input
                  type="text"
                  value={testMsg}
                  onChange={(e) => setTestMsg(e.target.value)}
                  placeholder="Enter message"
                  required
                />
              </div>

              <button type="submit" className="btn-submit" disabled={isSubmitting}>
                {isSubmitting ? 'Sending Request...' : 'Send POST Request'}
              </button>
            </form>

            {postResponse && (
              <div className="response-box success-box">
                <h4>✅ 201 Created Response from Server:</h4>
                <pre>{JSON.stringify(postResponse, null, 2)}</pre>
              </div>
            )}

            {postError && (
              <div className="response-box error-box">
                <h4>❌ Validation Error (422 Unprocessable Entity):</h4>
                <pre>{postError}</pre>
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>TestPilot – University Software Testing Platform • Day 3 Complete</p>
      </footer>
    </div>
  );
}
