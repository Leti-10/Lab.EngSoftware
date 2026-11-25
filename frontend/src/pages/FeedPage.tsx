import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ReviewItem } from '../components/ReviewSection'
import { Alert } from '../components/ui'
import { api } from '../lib/api'
import type { FeedItem } from '../lib/types'

export function FeedPage() {
  const [items, setItems] = useState<FeedItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api<FeedItem[]>('/feed')
      .then((data) => !cancelled && setItems(data))
      .catch((err: Error) => !cancelled && setError(err.message))
    return () => {
      cancelled = true
    }
  }, [])

  function replace(updated: FeedItem) {
    setItems((current) =>
      (current ?? []).map((item) => (item.id === updated.id ? { ...item, ...updated } : item)),
    )
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-3xl font-semibold">Feed</h1>
      <p className="mt-1 text-sm text-ink-soft">Resenhas das pessoas que você segue.</p>

      <div className="mt-6">
        {error && <Alert>{error}</Alert>}
        {items === null && !error && <p className="text-ink-soft">Carregando…</p>}
        {items?.length === 0 && (
          <p className="py-12 text-center text-ink-soft">
            Seu feed está vazio. Siga leitores nas resenhas da{' '}
            <Link to="/livros" className="font-medium text-blue-warm-600 hover:underline">
              estante
            </Link>{' '}
            para ver as novidades aqui.
          </p>
        )}
        {items && items.length > 0 && (
          <ul className="space-y-3">
            {items.map((item) => (
              <ReviewItem
                key={item.id}
                review={item}
                bookTitle={item.book_title ?? `Obra ${item.book_id}`}
                onChange={(review) => replace({ ...item, ...review })}
              />
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
