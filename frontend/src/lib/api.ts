const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) || 'http://localhost:8000'
const TOKEN_KEY = 'syncboard:token'

export function getToken(): string | null {
  return window.localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  code: string
  status: number

  constructor(message: string, code: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

interface ApiEnvelope<T> {
  success: boolean
  data: T | null
  error: { code: string; message: string } | null
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> | undefined),
  }

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  } catch {
    throw new ApiError('Could not reach the server. Is the backend running?', 'NETWORK_ERROR', 0)
  }

  let body: ApiEnvelope<T> | null = null
  try {
    body = (await response.json()) as ApiEnvelope<T>
  } catch {
    body = null
  }

  if (!response.ok || !body || !body.success) {
    throw new ApiError(
      body?.error?.message ?? `Request failed with status ${response.status}`,
      body?.error?.code ?? 'UNKNOWN_ERROR',
      response.status,
    )
  }

  return body.data as T
}

export const api = {
  get: <T>(path: string): Promise<T> => request<T>(path),
  post: <T>(path: string, json?: unknown): Promise<T> =>
    request<T>(path, {
      method: 'POST',
      body: json !== undefined ? JSON.stringify(json) : undefined,
    }),
  patch: <T>(path: string, json?: unknown): Promise<T> =>
    request<T>(path, {
      method: 'PATCH',
      body: json !== undefined ? JSON.stringify(json) : undefined,
    }),
  delete: <T>(path: string): Promise<T> => request<T>(path, { method: 'DELETE' }),
}
