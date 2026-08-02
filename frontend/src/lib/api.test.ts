import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api, ApiError, clearToken, getToken, setToken } from './api'

function jsonResponse(body: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => body,
  } as Response
}

describe('token storage', () => {
  beforeEach(() => window.localStorage.clear())

  it('round-trips a token through localStorage', () => {
    expect(getToken()).toBeNull()
    setToken('abc123')
    expect(getToken()).toBe('abc123')
    clearToken()
    expect(getToken()).toBeNull()
  })
})

describe('api client', () => {
  beforeEach(() => {
    window.localStorage.clear()
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns the data payload on a successful envelope', async () => {
    vi.mocked(fetch).mockResolvedValue(
      jsonResponse({ success: true, data: { id: 1 }, error: null }),
    )

    const result = await api.get<{ id: number }>('/boards')

    expect(result).toEqual({ id: 1 })
  })

  it('attaches an Authorization header when a token is stored', async () => {
    setToken('my-token')
    vi.mocked(fetch).mockResolvedValue(jsonResponse({ success: true, data: [], error: null }))

    await api.get('/boards')

    const [, options] = vi.mocked(fetch).mock.calls[0]
    const headers = options?.headers as Record<string, string>
    expect(headers.Authorization).toBe('Bearer my-token')
  })

  it('throws an ApiError using the envelope error when the request fails', async () => {
    vi.mocked(fetch).mockResolvedValue(
      jsonResponse(
        { success: false, data: null, error: { code: 'UNAUTHORIZED', message: 'nope' } },
        false,
        401,
      ),
    )

    await expect(api.get('/auth/me')).rejects.toMatchObject({
      message: 'nope',
      code: 'UNAUTHORIZED',
      status: 401,
    })
  })

  it('wraps network failures in an ApiError instead of throwing raw', async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(api.get('/boards')).rejects.toBeInstanceOf(ApiError)
  })

  it('sends a PATCH request with a JSON body for renames', async () => {
    vi.mocked(fetch).mockResolvedValue(
      jsonResponse({ success: true, data: { id: 1, name: 'New name' }, error: null }),
    )

    const result = await api.patch<{ id: number; name: string }>('/boards/1', { name: 'New name' })

    expect(result).toEqual({ id: 1, name: 'New name' })
    const [, options] = vi.mocked(fetch).mock.calls[0]
    expect(options?.method).toBe('PATCH')
    expect(options?.body).toBe(JSON.stringify({ name: 'New name' }))
  })
})
