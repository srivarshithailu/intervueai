// Tests for the auth store's sign-in and sign-out transitions, with the Firebase module and fetch mocked.

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { FirebaseProfile } from "../lib/firebase";

// Shared with the mocked module below; vi.hoisted makes it exist before vi.mock runs.
const fb = vi.hoisted(() => ({
  configured: true,
  listener: null as ((profile: FirebaseProfile | null) => void) | null,
  token: "token-123" as string | null,
  signOutUser: vi.fn(async () => {}),
}));

vi.mock("../lib/firebase", () => ({
  // A getter, because the mocked module is created once but tests change this value.
  get firebaseConfigured() {
    return fb.configured;
  },
  watchAuthState: (callback: (profile: FirebaseProfile | null) => void) => {
    fb.listener = callback;
    return () => {};
  },
  getIdToken: async () => fb.token,
  signOutUser: fb.signOutUser,
}));

function serverAuthMode(mode: string) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => new Response(JSON.stringify({ auth_mode: mode }), { status: 200 })),
  );
}

// A fresh store and api module per test, so state from one test never leaks into the next.
async function loadModules() {
  vi.resetModules();
  const store = await import("./authStore");
  const api = await import("../lib/api");
  return { useAuthStore: store.useAuthStore, buildHeaders: api.buildHeaders };
}

beforeEach(() => {
  fb.configured = true;
  fb.listener = null;
  fb.token = "token-123";
  fb.signOutUser.mockClear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("firebase mode", () => {
  it("waits for Firebase, then signs in and attaches the ID token", async () => {
    serverAuthMode("firebase");
    const { useAuthStore, buildHeaders } = await loadModules();
    await useAuthStore.getState().init();

    expect(useAuthStore.getState().mode).toBe("firebase");
    expect(useAuthStore.getState().loading).toBe(true);

    fb.listener?.({ uid: "u1", email: "asha@example.com", name: "Asha" });
    expect(useAuthStore.getState().loading).toBe(false);
    expect(useAuthStore.getState().user?.uid).toBe("u1");

    const headers = await buildHeaders();
    expect(headers.get("Authorization")).toBe("Bearer token-123");
    expect(headers.get("X-Dev-User")).toBeNull();
  });

  it("shows signed-out when Firebase reports no user", async () => {
    serverAuthMode("firebase");
    const { useAuthStore } = await loadModules();
    await useAuthStore.getState().init();
    fb.listener?.(null);
    expect(useAuthStore.getState().loading).toBe(false);
    expect(useAuthStore.getState().user).toBeNull();
  });

  it("signs out through Firebase", async () => {
    serverAuthMode("firebase");
    const { useAuthStore } = await loadModules();
    await useAuthStore.getState().init();
    fb.listener?.({ uid: "u1", email: "asha@example.com", name: "Asha" });

    await useAuthStore.getState().signOut();
    expect(fb.signOutUser).toHaveBeenCalledOnce();
    expect(useAuthStore.getState().user).toBeNull();
  });

  it("reports missing Firebase settings instead of failing silently", async () => {
    fb.configured = false;
    serverAuthMode("firebase");
    const { useAuthStore } = await loadModules();
    await useAuthStore.getState().init();
    expect(useAuthStore.getState().loading).toBe(false);
    expect(useAuthStore.getState().error).toMatch(/frontend\/\.env\.local/);
  });
});

describe("dev mode", () => {
  it("signs in and out with the dev header", async () => {
    serverAuthMode("dev");
    const { useAuthStore, buildHeaders } = await loadModules();
    await useAuthStore.getState().init();
    expect(useAuthStore.getState().user).toBeNull();

    useAuthStore.getState().signInDev("asha");
    expect(useAuthStore.getState().user?.uid).toBe("dev-asha");
    expect((await buildHeaders()).get("X-Dev-User")).toBe("asha");

    await useAuthStore.getState().signOut();
    expect(useAuthStore.getState().user).toBeNull();
    expect((await buildHeaders()).get("X-Dev-User")).toBeNull();
    expect(fb.signOutUser).not.toHaveBeenCalled();
  });
});

describe("server unreachable", () => {
  it("shows an error and can try again", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => Promise.reject(new TypeError("Failed to fetch"))));
    const { useAuthStore } = await loadModules();
    await useAuthStore.getState().init();
    expect(useAuthStore.getState().error).toMatch(/Cannot reach the server/);

    serverAuthMode("dev");
    await useAuthStore.getState().init();
    expect(useAuthStore.getState().error).toBeNull();
    expect(useAuthStore.getState().mode).toBe("dev");
  });
});
