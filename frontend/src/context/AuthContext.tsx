import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api, setToken, getToken } from '@/lib/api'
import type { TokenResponse, User } from '@/types'

interface AuthCtx {
  user: User | null
  loading: boolean
  login: (email: string, password: string, remember: boolean) => Promise<void>
  logout: () => void
}

const Ctx = createContext<AuthCtx | undefined>(undefined)
const USER_KEY = 'vanguardian.user'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  })
  const [loading, setLoading] = useState(true)

  // Revalida a sessão contra a API se houver token.
  useEffect(() => {
    let active = true
    async function check() {
      if (!getToken()) {
        setLoading(false)
        return
      }
      try {
        const me = await api.get<User>('/auth/me')
        if (active) {
          setUser(me)
          localStorage.setItem(USER_KEY, JSON.stringify(me))
        }
      } catch {
        if (active) {
          setUser(null)
          localStorage.removeItem(USER_KEY)
        }
      } finally {
        if (active) setLoading(false)
      }
    }
    check()
    return () => {
      active = false
    }
  }, [])

  async function login(email: string, password: string, remember: boolean) {
    const res = await api.post<TokenResponse>('/auth/login', {
      email,
      password,
      remember_me: remember,
    })
    setToken(res.access_token)
    setUser(res.user)
    localStorage.setItem(USER_KEY, JSON.stringify(res.user))
  }

  function logout() {
    setToken(null)
    setUser(null)
    localStorage.removeItem(USER_KEY)
  }

  return (
    <Ctx.Provider value={{ user, loading, login, logout }}>{children}</Ctx.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth deve ser usado dentro de AuthProvider')
  return ctx
}
