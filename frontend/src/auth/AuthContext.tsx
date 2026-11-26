import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { api, ApiError, clearLegacyAuthToken } from '../lib/api'
import type { AuthResponse, Book, User } from '../lib/types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  favorites: Book[]
  favoritesLoading: boolean
  favoritesError: string | null
  toggleFavorite: (book: Book) => Promise<void>
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [favorites, setFavorites] = useState<Book[]>([])
  const [favoritesLoading, setFavoritesLoading] = useState(true)
  const [favoritesError, setFavoritesError] = useState<string | null>(null)
  const [sessionError, setSessionError] = useState<string | null>(null)
  const authRequestId = useRef(0)

  useEffect(() => {
    clearLegacyAuthToken()
    const requestId = ++authRequestId.current
    api<User>('/auth/me')
      .then((authenticatedUser) => {
        if (requestId === authRequestId.current) setUser(authenticatedUser)
      })
      .catch((error: Error) => {
        if (requestId !== authRequestId.current) return
        setUser(null)
        setFavoritesLoading(false)
        if (error instanceof ApiError && error.status === 401) {
          setSessionError(null)
        } else {
          setSessionError(error.message)
        }
      })
      .finally(() => {
        if (requestId === authRequestId.current) setLoading(false)
      })
    return () => {
      authRequestId.current += 1
    }
  }, [])

  useEffect(() => {
    let cancelled = false

    if (!user) return
    api<Book[]>('/votes/favorites')
      .then((books) => {
        if (!cancelled) setFavorites(books)
      })
      .catch((error: Error) => {
        if (!cancelled) setFavoritesError(error.message)
      })
      .finally(() => {
        if (!cancelled) setFavoritesLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [user])

  const authenticate = useCallback(async (path: string, body: object) => {
    const requestId = ++authRequestId.current
    setLoading(true)
    setSessionError(null)
    try {
      const data = await api<AuthResponse>(path, {
        method: 'POST',
        body: JSON.stringify(body),
      })
      if (requestId !== authRequestId.current) return
      setFavorites([])
      setFavoritesLoading(true)
      setFavoritesError(null)
      setUser(data.user)
    } finally {
      if (requestId === authRequestId.current) setLoading(false)
    }
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

  const logout = useCallback(async () => {
    const requestId = ++authRequestId.current
    await api<void>('/auth/logout', { method: 'POST' })
    if (requestId !== authRequestId.current) return
    setUser(null)
    setFavorites([])
    setFavoritesLoading(false)
    setFavoritesError(null)
    setSessionError(null)
  }, [])

  const updateUser = useCallback((updated: User) => setUser(updated), [])

  const toggleFavorite = useCallback(
    async (book: Book) => {
      const isFavorite = favorites.some((favorite) => favorite.id === book.id)
      await api<void>(`/votes/favorites/${book.id}`, {
        method: isFavorite ? 'DELETE' : 'PUT',
      })
      setFavorites((current) =>
        isFavorite ? current.filter((favorite) => favorite.id !== book.id) : [...current, book],
      )
      setFavoritesError(null)
    },
    [favorites],
  )

  const value = useMemo(
    () => ({
      user,
      loading,
      favorites,
      favoritesLoading,
      favoritesError,
      toggleFavorite,
      login,
      register,
      logout,
      updateUser,
    }),
    [
      user,
      loading,
      favorites,
      favoritesLoading,
      favoritesError,
      toggleFavorite,
      login,
      register,
      logout,
      updateUser,
    ],
  )

  return (
    <AuthContext.Provider value={value}>
      {sessionError && (
        <p role="alert" className="mx-auto max-w-7xl px-4 py-2 text-sm text-red-700">
          Não foi possível validar a sessão: {sessionError}
        </p>
      )}
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve ser usado dentro de AuthProvider')
  return context
}

export function useOptionalAuth() {
  return useContext(AuthContext)
}
