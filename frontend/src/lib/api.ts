// Fetch wrapper for the backend: adds the auth header to every call and turns
// error bodies ({error: {code, message}}) into ApiError so pages can show plain messages.

type TokenGetter = () => Promise<string | null>;

// Set by the auth store. Returns a fresh Firebase ID token, or null when signed out.
let getToken: TokenGetter = async () => null;
// Only used when the backend runs AUTH_MODE=dev; the backend ignores it otherwise.
let devUser: string | null = null;

export function setTokenGetter(fn: TokenGetter): void {
  getToken = fn;
}

export function setDevUser(id: string | null): void {
  devUser = id;
}

export class ApiError extends Error {
  status: number;
  code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export async function buildHeaders(extra?: HeadersInit): Promise<Headers> {
  const headers = new Headers(extra);
  const token = await getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  } else if (devUser) {
    headers.set("X-Dev-User", devUser);
  }
  return headers;
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = await buildHeaders(options.headers);
  if (options.body && !(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, "network", "Cannot reach the server. Check your connection and that the backend is running.");
  }

  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const error = (body as { error?: { code?: string; message?: string } } | null)?.error;
    throw new ApiError(
      response.status,
      error?.code ?? "error",
      error?.message ?? `Request failed (${response.status}).`,
    );
  }
  return body as T;
}
