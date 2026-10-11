// Firebase setup and sign-in helpers. M0 stub: real Firebase login is built in M1 (see AGENTS.md).

export const firebaseConfigured = Boolean(import.meta.env.VITE_FIREBASE_API_KEY);

function notReady(): never {
  throw new Error("Firebase sign-in is not built yet. Use dev sign-in for now.");
}

export async function signInWithGoogle(): Promise<void> {
  notReady();
}

export async function signInWithEmail(_email: string, _password: string): Promise<void> {
  notReady();
}

export async function signUpWithEmail(_email: string, _password: string): Promise<void> {
  notReady();
}

export async function signOutUser(): Promise<void> {
  // Nothing to sign out of until Firebase is wired in.
}
