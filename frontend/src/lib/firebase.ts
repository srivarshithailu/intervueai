// Firebase setup and the sign-in helpers the app uses. The only file that imports the Firebase SDK.
// Config comes from frontend/.env.local (VITE_FIREBASE_*). Without it, Firebase stays off and dev sign-in is used.

import { initializeApp } from "firebase/app";
import {
  createUserWithEmailAndPassword,
  getAuth,
  GoogleAuthProvider,
  onAuthStateChanged,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  type Auth,
  type User,
} from "firebase/auth";

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

export const firebaseConfigured = Object.values(config).every(Boolean);

// null when the config is missing, so importing this file never crashes the app.
export const auth: Auth | null = firebaseConfigured ? getAuth(initializeApp(config)) : null;

function requireAuth(): Auth {
  if (!auth) throw new Error("Firebase is not configured. Fill in frontend/.env.local.");
  return auth;
}

export interface FirebaseProfile {
  uid: string;
  email: string;
  name: string;
}

function toProfile(user: User): FirebaseProfile {
  return { uid: user.uid, email: user.email ?? "", name: user.displayName ?? "" };
}

/** Calls back with the signed-in profile (or null) now and on every change. Returns an unsubscribe function. */
export function watchAuthState(callback: (profile: FirebaseProfile | null) => void): () => void {
  return onAuthStateChanged(requireAuth(), (user) => callback(user ? toProfile(user) : null));
}

/** A fresh ID token for API calls. Firebase refreshes it automatically shortly before it expires. */
export async function getIdToken(): Promise<string | null> {
  const user = auth?.currentUser;
  return user ? user.getIdToken() : null;
}

export async function signInWithGoogle(): Promise<void> {
  await signInWithPopup(requireAuth(), new GoogleAuthProvider());
}

export async function signInWithEmail(email: string, password: string): Promise<void> {
  await signInWithEmailAndPassword(requireAuth(), email, password);
}

export async function signUpWithEmail(email: string, password: string): Promise<void> {
  await createUserWithEmailAndPassword(requireAuth(), email, password);
}

export async function resetPassword(email: string): Promise<void> {
  await sendPasswordResetEmail(requireAuth(), email);
}

export async function signOutUser(): Promise<void> {
  if (auth) await signOut(auth);
}
