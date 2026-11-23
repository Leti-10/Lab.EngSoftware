import { BookCheck, BookOpen, Bookmark } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'
import type { Reading, ReadingKind } from '../lib/types'
import { Alert } from './ui'

const OPTIONS: { value: ReadingKind; label: string; icon: typeof Bookmark }[] = [
  { value: 'want_to_read', label: 'Quero ler', icon: Bookmark },
  { value: 'reading', label: 'Lendo', icon: BookOpen },
  { value: 'read', label: 'Lido', icon: BookCheck },
]

export function ReadingStatus({ bookId }: { bookId: number }) {
  const { user } = useAuth()
  const [current, setCurrent] = useState<ReadingKind | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) return
    let cancelled = false
    api<Reading[]>(`/readings?book_id=${bookId}`)
      .then((data) => !cancelled && setCurrent(data[0]?.status ?? null))
      .catch(() => undefined)
    return () => {
      cancelled = true
    }
  }, [bookId, user])

  async function choose(value: ReadingKind) {
    setError(null)
    setBusy(true)
    try {
      if (current === value) {
        await api(`/readings/${bookId}`, { method: 'DELETE' })
        setCurrent(null)
      } else {
        const saved = await api<Reading>(`/readings/${bookId}`, {
          method: 'PUT',
          body: JSON.stringify({ status: value }),
        })
        setCurrent(saved.status)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível salvar.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <div
        role="group"
        aria-label="Status de leitura"
        className="grid grid-cols-3 divide-x divide-cream-300"
      >
        {OPTIONS.map(({ value, label, icon: Icon }) => {
          const active = current === value
          return (
            <button
              key={value}
              type="button"
              aria-pressed={active}
              disabled={!user || busy}
              title={user ? undefined : 'Entre para marcar'}
              onClick={() => choose(value)}
              className={`flex flex-col items-center gap-2 px-2 py-4 text-xs transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
                active
                  ? 'bg-blue-warm-600 text-cream-50'
                  : 'text-ink hover:bg-cream-200 disabled:hover:bg-transparent'
              }`}
            >
              <Icon aria-hidden="true" className="size-6" />
              {label}
            </button>
          )
        })}
      </div>
      {error && (
        <div className="p-3">
          <Alert>{error}</Alert>
        </div>
      )}
    </div>
  )
}
