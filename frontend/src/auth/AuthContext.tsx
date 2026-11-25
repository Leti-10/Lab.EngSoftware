import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { api, tokenStorage } from '../lib/api'
import type { Book, TokenResponse, User } from '../lib/types'

interface AuthContextValue {
  user: User | null
  loading: boolean
  favorites: Book[]
  favoritesLoading: boolean
  favoritesError: string | null
  toggleFavorite: (book: Book) => Promise<void>
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(() => tokenStorage.get() !== null)
  const [favorites, setFavorites] = useState<Book[]>([])
  const [favoritesLoading, setFavoritesLoading] = useState(() => tokenStorage.get() !== null)
  const [favoritesError, setFavoritesError] = useState<string | null>(null)

  useEffect(() => {
    if (!tokenStorage.get()) return
    api<User>('/auth/me')
      .then(setUser)
      .catch(() => {
        tokenStorage.clear()
        setFavoritesLoading(false)
      })
      .finally(() => setLoading(false))
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
    const data = await api<TokenResponse>(path, { method: 'POST', body: JSON.stringify(body) })
    tokenStorage.set(data.access_token)
    setFavorites([])
    setFavoritesLoading(true)
    setFavoritesError(null)
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
    setFavorites([])
    setFavoritesLoading(false)
    setFavoritesError(null)
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

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve ser usado dentro de AuthProvider')
  return context
}

export function useOptionalAuth() {
  return useContext(AuthContext)
}
