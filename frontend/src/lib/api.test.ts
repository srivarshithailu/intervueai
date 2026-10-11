// Tests for the API wrapper's auth header choice.

import { afterEach, describe, expect, it } from "vitest";
import { buildHeaders, setDevUser, setTokenGetter } from "./api";

afterEach(() => {
  setTokenGetter(async () => null);
  setDevUser(null);
});

describe("buildHeaders", () => {
  it("sends a Bearer token when signed in", async () => {
    setTokenGetter(async () => "abc");
    setDevUser("asha");
    const headers = await buildHeaders();
    expect(headers.get("Authorization")).toBe("Bearer abc");
    expect(headers.get("X-Dev-User")).toBeNull();
  });

  it("falls back to the dev header when there is no token", async () => {
    setDevUser("asha");
    const headers = await buildHeaders();
    expect(headers.get("X-Dev-User")).toBe("asha");
    expect(headers.get("Authorization")).toBeNull();
  });

  it("sends no auth header when signed out", async () => {
    const headers = await buildHeaders({ Accept: "application/json" });
    expect(headers.get("Authorization")).toBeNull();
    expect(headers.get("X-Dev-User")).toBeNull();
    expect(headers.get("Accept")).toBe("application/json");
  });
});
