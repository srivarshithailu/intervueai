// Who is signed in, shared across pages (Zustand store).
// M0 stub: only "dev sign-in" (backend AUTH_MODE=dev). Firebase replaces this in M1.

import { create } from "zustand";
import { setDevUser } from "../lib/api";
import { signOutUser } from "../lib/firebase";

const DEV_USER_KEY = "intervueai.devUser";

export interface AuthUser {
  uid: string;
  name: string;
}

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  signInDev: (name: string) => void;
  signOut: () => Promise<void>;
}

// localStorage can throw (private mode, blocked storage); dev sign-in still works for this tab.
function readSavedDevUser(): string | null {
  try {
    return localStorage.getItem(DEV_USER_KEY);
  } catch {
    return null;
  }
}

function saveDevUser(name: string | null): void {
  try {
    if (name) localStorage.setItem(DEV_USER_KEY, name);
    else localStorage.removeItem(DEV_USER_KEY);
  } catch {
    // Not fatal: the user just signs in again after a refresh.
  }
}

const savedName = readSavedDevUser();
setDevUser(savedName);

export const useAuthStore = create<AuthState>((set) => ({
  user: savedName ? { uid: `dev-${savedName}`, name: savedName } : null,
  loading: false,
  error: null,

  signInDev: (name) => {
    setDevUser(name);
    saveDevUser(name);
    set({ user: { uid: `dev-${name}`, name }, error: null });
  },

  signOut: async () => {
    await signOutUser();
    setDevUser(null);
    saveDevUser(null);
    set({ user: null });
  },
}));
