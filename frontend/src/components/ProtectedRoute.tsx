// Guards pages that need a signed-in user. M0 stub: lets everything through; M1 adds the redirect to /login.

import type { ReactNode } from "react";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  return children;
}
