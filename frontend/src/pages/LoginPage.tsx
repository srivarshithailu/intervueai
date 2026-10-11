// Sign-in page. M0 stub: a dev sign-in form for AUTH_MODE=dev. Firebase login replaces it in M1.

import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router";
import Notice from "../components/Notice";
import { useAuthStore } from "../store/authStore";

// Same rule as the backend (app/deps.py), so the user sees the problem before a 401.
const DEV_NAME_PATTERN = /^[A-Za-z0-9_.@-]{1,64}$/;

export default function LoginPage() {
  const signInDev = useAuthStore((state) => state.signInDev);
  const navigate = useNavigate();
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
    navigate("/");
  }

  return (
    <>
      <h1>Sign in</h1>
      <p className="muted">Google and email sign-in arrive in the next milestone. For now, use dev sign-in.</p>
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
