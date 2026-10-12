// Who is signed in, shared across pages (Zustand store).
// The backend decides the login method: /api/health says AUTH_MODE "firebase" or "dev", and this store follows it,
// so the frontend never sends a kind of login the backend would reject.

import { create } from "zustand";
import { apiFetch, setDevUser, setTokenGetter } from "../lib/api";
import { firebaseConfigured, getIdToken, signOutUser, watchAuthState } from "../lib/firebase";

const DEV_USER_KEY = "intervueai.devUser";

export type AuthMode = "dev" | "firebase";

export interface AuthUser {
  uid: string;
  name: string;
  email: string;
}

interface AuthState {
  mode: AuthMode | null; // null until /api/health has answered
  user: AuthUser | null;
  loading: boolean; // true until we know the mode and the first sign-in state
  error: string | null; // a setup problem, shown on the login page
  init: () => Promise<void>;
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

function devAuthUser(name: string): AuthUser {
  return { uid: `dev-${name}`, name, email: `${name}@dev.local` };
}

// init() runs once per page load; after a setup error it may run again ("Try again" on the login page).
let started = false;

export const useAuthStore = create<AuthState>((set, get) => ({
  mode: null,
  user: null,
  loading: true,
  error: null,

  init: async () => {
    if (started) return;
    started = true;
    set({ loading: true, error: null });

    let mode: string;
    try {
      mode = (await apiFetch<{ auth_mode: string }>("/health")).auth_mode;
    } catch {
      started = false;
      set({ loading: false, error: "Cannot reach the server. Check that the backend is running, then try again." });
      return;
    }

    if (mode === "firebase") {
      setDevUser(null); // never send the dev header to a Firebase backend
      if (!firebaseConfigured) {
        started = false;
        set({
          mode,
          loading: false,
          error: "The server uses Firebase sign-in, but the Firebase settings in frontend/.env.local are missing.",
        });
        return;
      }
      setTokenGetter(getIdToken);
      set({ mode });
      // Fires once with the restored session (Firebase keeps it across refreshes), then on every change.
      watchAuthState((profile) => {
        set({
          user: profile ? { uid: profile.uid, name: profile.name, email: profile.email } : null,
          loading: false,
        });
      });
      return;
    }

    if (mode === "dev") {
      const saved = readSavedDevUser();
      setDevUser(saved);
      set({ mode, user: saved ? devAuthUser(saved) : null, loading: false });
      return;
    }

    started = false;
    set({ loading: false, error: "The server reported an unknown sign-in mode." });
  },

  signInDev: (name) => {
    setDevUser(name);
    saveDevUser(name);
    set({ user: devAuthUser(name), error: null });
  },

  signOut: async () => {
    if (get().mode === "firebase") {
      await signOutUser();
    } else {
      setDevUser(null);
      saveDevUser(null);
    }
    set({ user: null });
  },
}));
