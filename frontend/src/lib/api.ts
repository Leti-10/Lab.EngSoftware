export const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const TOKEN_KEY = 'estante.token'

export const tokenStorage = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

function extractMessage(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string; loc?: unknown[] }
      const field = first.loc?.[first.loc.length - 1]
      return field ? `${String(field)}: ${first.msg}` : (first.msg ?? fallback)
    }
  }
  return fallback
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const token = tokenStorage.get()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, headers })
  } catch (err) {
    if ((err as Error)?.name === 'AbortError') throw err
    throw new ApiError(0, 'Não foi possível conectar ao servidor.')
  }

  const body = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, extractMessage(body, 'Algo deu errado. Tente novamente.'))
  }
  return body as T
}
