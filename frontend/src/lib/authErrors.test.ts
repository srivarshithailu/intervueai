// Tests that Firebase error codes become friendly messages and raw codes never leak to the user.

import { describe, expect, it } from "vitest";
import { friendlyAuthError } from "./authErrors";

describe("friendlyAuthError", () => {
  it.each([
    ["auth/invalid-credential", "Email or password is incorrect."],
    ["auth/email-already-in-use", "An account with this email already exists. Sign in instead."],
    ["auth/weak-password", "Please choose a stronger password (at least 6 characters)."],
    ["auth/popup-closed-by-user", "The Google sign-in window was closed before finishing."],
    ["auth/network-request-failed", "Network problem. Check your connection and try again."],
  ])("maps %s", (code, message) => {
    expect(friendlyAuthError({ code })).toBe(message);
  });

  it("uses a generic message for unknown codes and non-errors", () => {
    expect(friendlyAuthError({ code: "auth/something-new" })).toBe("Sign-in failed. Please try again.");
    expect(friendlyAuthError("boom")).toBe("Sign-in failed. Please try again.");
    expect(friendlyAuthError(null)).not.toMatch(/auth\//);
  });
});
