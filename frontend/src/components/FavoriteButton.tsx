import { Heart } from 'lucide-react'
import { useState } from 'react'
import type { Book } from '../lib/types'
import { useOptionalAuth } from '../auth/AuthContext'

export function FavoriteButton({
  book,
  className = '',
  compact = false,
}: {
  book: Book
  className?: string
  compact?: boolean
}) {
  const auth = useOptionalAuth()
  const [confirming, setConfirming] = useState(false)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pulseKey, setPulseKey] = useState(0)

  if (!auth?.user) return null

  const authenticated = auth
  const isFavorite = authenticated.favorites.some((favorite) => favorite.id === book.id)
  const label = confirming ? 'Confirmar?' : isFavorite ? 'Desfavoritar' : 'Favoritar'

  async function handleClick() {
    if (isFavorite && !confirming) {
      setConfirming(true)
      return
    }

    setPending(true)
    setError(null)
    try {
      await authenticated.toggleFavorite(book)
      setConfirming(false)
      if (!isFavorite) setPulseKey((current) => current + 1)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível atualizar favoritos.')
      setConfirming(false)
    } finally {
      setPending(false)
    }
  }

  return (
    <span className={className}>
      <button
        type="button"
        aria-label={label}
        title={label}
        aria-pressed={isFavorite}
        disabled={pending || authenticated.favoritesLoading}
        onClick={handleClick}
        className={`inline-flex cursor-pointer items-center gap-1.5 rounded-full border border-cream-300 bg-cream-50/95 py-2 text-sm font-medium text-ink shadow-sm transition-colors hover:bg-cream-200 disabled:cursor-not-allowed disabled:opacity-60 ${compact && !confirming ? 'px-2' : 'px-3'}`}
      >
        <Heart
          key={pulseKey}
          aria-hidden="true"
          className={`size-4 ${isFavorite ? 'fill-danger text-danger' : 'text-ink-soft'} ${pulseKey > 0 ? 'favorite-pulse' : ''}`}
        />
        {(!compact || confirming) && <span>{label}</span>}
      </button>
      {error && (
        <span role="alert" className="mt-1 block max-w-48 text-xs text-danger">
          {error}
        </span>
      )}
    </span>
  )
}
