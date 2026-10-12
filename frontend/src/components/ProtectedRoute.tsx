// Guards pages that need a signed-in user: waits while sign-in state loads, sends signed-out visitors to /login.

import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router";
import { useAuthStore } from "../store/authStore";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const user = useAuthStore((state) => state.user);
  const loading = useAuthStore((state) => state.loading);
  const location = useLocation();

  if (loading) {
    return <p className="muted">Checking sign-in...</p>;
  }
  if (!user) {
    // Remember where they were going so login can send them back there.
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}
