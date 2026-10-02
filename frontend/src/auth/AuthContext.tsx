import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { api, tokenStorage } from '../lib/api'
import type { TokenResponse, User } from '../lib/types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(() => tokenStorage.get() !== null)

  useEffect(() => {
    if (!tokenStorage.get()) return
    api<User>('/auth/me')
      .then(setUser)
      .catch(() => tokenStorage.clear())
      .finally(() => setLoading(false))
  }, [])

  const authenticate = useCallback(async (path: string, body: object) => {
    const data = await api<TokenResponse>(path, { method: 'POST', body: JSON.stringify(body) })
    tokenStorage.set(data.access_token)
    setUser(data.user)
  }, [])

  const login = useCallback(
    (email: string, password: string) => authenticate('/auth/login', { email, password }),
    [authenticate],
  )

  const register = useCallback(
    (username: string, email: string, password: string) =>
      authenticate('/auth/register', { username, email, password }),
    [authenticate],
  )

  const logout = useCallback(() => {
    tokenStorage.clear()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve ser usado dentro de AuthProvider')
  return context
}
