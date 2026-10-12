// Firebase sign-in: Google button, email/password sign in or create account, and password reset.
// On success Firebase updates the auth store, and LoginPage redirects; this form only starts the sign-in.

import { useState, type FormEvent } from "react";
import Notice from "./Notice";
import { friendlyAuthError } from "../lib/authErrors";
import { resetPassword, signInWithEmail, signInWithGoogle, signUpWithEmail } from "../lib/firebase";

type Step = "signIn" | "createAccount";

export default function FirebaseSignInForm() {
  const [step, setStep] = useState<Step>("signIn");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState<string | null>(null); // which action is running, for the button label
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  async function run(action: string, work: () => Promise<void>) {
    setBusy(action);
    setError(null);
    setInfo(null);
    try {
      await work();
    } catch (err) {
      setError(friendlyAuthError(err));
    } finally {
      setBusy(null);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = email.trim();
    if (step === "signIn") {
      void run("email", () => signInWithEmail(trimmed, password));
    } else {
      void run("email", () => signUpWithEmail(trimmed, password));
    }
  }

  function handleForgotPassword() {
    const trimmed = email.trim();
    if (!trimmed) {
      setInfo(null);
      setError("Enter your email address above first, then choose Forgot password.");
      return;
    }
    void run("reset", async () => {
      await resetPassword(trimmed);
      // Same words whether or not the account exists, so the page does not reveal who has an account.
      setInfo(`If an account exists for ${trimmed}, a password reset email is on its way. Check your inbox and spam folder.`);
    });
  }

  function switchStep() {
    setStep(step === "signIn" ? "createAccount" : "signIn");
    setError(null);
    setInfo(null);
  }

  const creating = step === "createAccount";
  const disabled = busy !== null;

  return (
    <>
      <h1>{creating ? "Create account" : "Sign in"}</h1>
      {error && <Notice warning>{error}</Notice>}
      {info && <Notice>{info}</Notice>}

      <div className="button-row">
        <button type="button" onClick={() => void run("google", signInWithGoogle)} disabled={disabled}>
          {busy === "google" ? "Opening Google..." : "Continue with Google"}
        </button>
      </div>

      <p className="muted">Or use your email address:</p>
      <form className="form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete={creating ? "new-password" : "current-password"}
            minLength={creating ? 6 : undefined}
            required
          />
          {creating && <span className="muted">At least 6 characters.</span>}
        </div>
        <div className="button-row">
          <button type="submit" disabled={disabled}>
            {busy === "email" ? "Please wait..." : creating ? "Create account" : "Sign in"}
          </button>
          {!creating && (
            <button type="button" onClick={handleForgotPassword} disabled={disabled}>
              {busy === "reset" ? "Sending..." : "Forgot password"}
            </button>
          )}
        </div>
      </form>

      <p>
        {creating ? "Already have an account?" : "New here?"}{" "}
        <button type="button" onClick={switchStep} disabled={disabled}>
          {creating ? "Sign in instead" : "Create an account"}
        </button>
      </p>
    </>
  );
}
