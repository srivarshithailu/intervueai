// Home (dashboard). M0: shows server health and the signed-in user to prove the frontend-backend path works.
// Later: past reports table, start interview, delete my data.

import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import Notice from "../components/Notice";
import { apiFetch, ApiError } from "../lib/api";
import { useAuthStore } from "../store/authStore";

interface Health {
  status: string;
  llm_chain: string[];
  stt_chain: string[];
  auth_mode: string;
  database: string;
}

interface Me {
  user_id: string;
  email: string;
  name: string;
}

function messageOf(error: unknown): string {
  return error instanceof ApiError ? error.message : "Something went wrong.";
}

export default function HomePage() {
  const signOut = useAuthStore((state) => state.signOut);
  const navigate = useNavigate();
  const [health, setHealth] = useState<Health | null>(null);
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Health>("/health")
      .then(setHealth)
      .catch((err: unknown) => setError(messageOf(err)));
    apiFetch<Me>("/me")
      .then(setMe)
      .catch((err: unknown) => setError(messageOf(err)));
  }, []);

  async function handleSignOut() {
    await signOut();
    navigate("/login");
  }

  return (
    <>
      <h1>Home</h1>
      {error && <Notice warning>{error}</Notice>}
      {me && <p>Signed in as {me.name || me.email}.</p>}

      <div className="button-row">
        <Link className="button" to="/new">
          Start new interview
        </Link>
        <Link className="button" to="/diagnostics">
          Diagnostics
        </Link>
        <button type="button" onClick={handleSignOut}>
          Sign out
        </button>
      </div>

      <h2>Past reports</h2>
      <p className="muted">No reports yet.</p>

      <h2>Server status</h2>
      {health ? (
        <dl className="facts">
          <dt>Status</dt>
          <dd>{health.status}</dd>
          <dt>Database</dt>
          <dd>{health.database}</dd>
          <dt>LLM chain</dt>
          <dd>{health.llm_chain.join(", ")}</dd>
          <dt>Speech-to-text chain</dt>
          <dd>{health.stt_chain.join(", ")}</dd>
          <dt>Auth mode</dt>
          <dd>{health.auth_mode}</dd>
        </dl>
      ) : (
        <p className="muted">Checking...</p>
      )}
    </>
  );
}
