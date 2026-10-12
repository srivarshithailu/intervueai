// Sign-in page. Shows Firebase sign-in or dev sign-in, whichever the backend uses,
// and sends the user on once they are signed in.

import { Navigate, useLocation } from "react-router";
import DevSignInForm from "../components/DevSignInForm";
import FirebaseSignInForm from "../components/FirebaseSignInForm";
import Notice from "../components/Notice";
import { useAuthStore } from "../store/authStore";

export default function LoginPage() {
  const mode = useAuthStore((state) => state.mode);
  const user = useAuthStore((state) => state.user);
  const loading = useAuthStore((state) => state.loading);
  const error = useAuthStore((state) => state.error);
  const init = useAuthStore((state) => state.init);
  const location = useLocation();

  if (loading) {
    return <p className="muted">Checking sign-in...</p>;
  }
  if (user) {
    const from = (location.state as { from?: string } | null)?.from;
    return <Navigate to={from && from !== "/login" ? from : "/"} replace />;
  }
  if (error) {
    return (
      <>
        <h1>Sign in</h1>
        <Notice warning>{error}</Notice>
        <div className="button-row">
          <button type="button" onClick={() => void init()}>
            Try again
          </button>
        </div>
      </>
    );
  }
  return mode === "firebase" ? <FirebaseSignInForm /> : <DevSignInForm />;
}
