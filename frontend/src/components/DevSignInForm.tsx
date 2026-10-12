// Dev sign-in form, shown only when the backend runs AUTH_MODE=dev (local development without Firebase).

import { useState, type FormEvent } from "react";
import Notice from "./Notice";
import { useAuthStore } from "../store/authStore";

// Same rule as the backend (app/deps.py), so the user sees the problem before a 401.
const DEV_NAME_PATTERN = /^[A-Za-z0-9_.@-]{1,64}$/;

export default function DevSignInForm() {
  const signInDev = useAuthStore((state) => state.signInDev);
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = name.trim();
    if (!DEV_NAME_PATTERN.test(trimmed)) {
      setError("Use 1 to 64 letters, numbers, dots, dashes, underscores or @. No spaces.");
      return;
    }
    signInDev(trimmed);
  }

  return (
    <>
      <h1>Sign in (dev mode)</h1>
      <p className="muted">The server is in development login mode. Any name works; no password is needed.</p>
      {error && <Notice warning>{error}</Notice>}
      <form className="form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="dev-name">Dev user name</label>
          <input id="dev-name" value={name} onChange={(event) => setName(event.target.value)} autoComplete="username" />
        </div>
        <div className="button-row">
          <button type="submit">Continue (dev mode)</button>
        </div>
      </form>
    </>
  );
}
