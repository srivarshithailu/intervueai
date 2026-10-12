// Turns Firebase sign-in errors into friendly sentences. Raw Firebase codes are never shown to users.

const MESSAGES: Record<string, string> = {
  "auth/invalid-credential": "Email or password is incorrect.",
  "auth/wrong-password": "Email or password is incorrect.",
  "auth/user-not-found": "Email or password is incorrect.",
  "auth/invalid-email": "That email address does not look right.",
  "auth/missing-password": "Please enter your password.",
  "auth/email-already-in-use": "An account with this email already exists. Sign in instead.",
  "auth/weak-password": "Please choose a stronger password (at least 6 characters).",
  "auth/password-does-not-meet-requirements": "Please choose a stronger password.",
  "auth/popup-closed-by-user": "The Google sign-in window was closed before finishing.",
  "auth/cancelled-popup-request": "The Google sign-in window was closed before finishing.",
  "auth/popup-blocked": "Your browser blocked the Google sign-in window. Allow pop-ups for this site and try again.",
  "auth/network-request-failed": "Network problem. Check your connection and try again.",
  "auth/too-many-requests": "Too many attempts. Please wait a few minutes and try again.",
  "auth/user-disabled": "This account has been disabled.",
  "auth/operation-not-allowed": "This sign-in method is not enabled for the project.",
  "auth/unauthorized-domain": "This site address is not allowed to sign in. Add it under Firebase Authentication > Settings.",
  "auth/invalid-api-key": "The Firebase settings in frontend/.env.local are not valid.",
};

const FALLBACK = "Sign-in failed. Please try again.";

export function friendlyAuthError(error: unknown): string {
  const code = typeof error === "object" && error !== null && "code" in error ? String(error.code) : "";
  return MESSAGES[code] ?? FALLBACK;
}
