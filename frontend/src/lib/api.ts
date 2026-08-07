// Cliente de API para o backend FastAPI do VANGUARDIAN.
// Base: VITE_API_BASE_URL em produção; em dev, o proxy /api do Vite → :8000.

const BASE = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || '/api'
const TOKEN_KEY = 'vanguardian.token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}
export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let resp: Response
  try {
    resp = await fetch(`${BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new ApiError(0, 'Não foi possível conectar à API. Verifique se o backend está no ar.')
  }

  if (resp.status === 401) {
    setToken(null)
    throw new ApiError(401, 'Sessão expirada. Faça login novamente.')
  }

  if (!resp.ok) {
    let detail = `Erro ${resp.status}`
    try {
      const data = await resp.json()
      detail = data.detail || detail
    } catch {
      /* corpo não-JSON */
    }
    throw new ApiError(resp.status, detail)
  }

  if (resp.status === 204) return undefined as T
  return (await resp.json()) as T
}

export const api = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body?: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body?: unknown) => request<T>('PUT', path, body),
  del: <T>(path: string) => request<T>('DELETE', path),
}
