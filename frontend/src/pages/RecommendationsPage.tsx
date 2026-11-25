import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BookCard } from '../components/BookCard'
import { Alert } from '../components/ui'
import { api } from '../lib/api'
import type { Recommendation } from '../lib/types'

export function RecommendationsPage() {
  const [items, setItems] = useState<Recommendation[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api<Recommendation[]>('/recommendations')
      .then((data) => !cancelled && setItems(data))
      .catch((err: Error) => !cancelled && setError(err.message))
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div>
      <h1 className="text-3xl font-semibold">Recomendações</h1>
      <p className="mt-1 text-sm text-ink-soft">
        Obras escolhidas com base nas suas avaliações e leituras.
      </p>

      <div className="mt-8">
        {error && <Alert>{error}</Alert>}
        {items === null && !error && <p className="text-ink-soft">Carregando…</p>}
        {items?.length === 0 && (
          <p className="py-12 text-center text-ink-soft">
            Ainda não temos o que recomendar. Avalie obras com 4 ou 5 estrelas ou marque o que está
            lendo na{' '}
            <Link to="/livros" className="font-medium text-blue-warm-600 hover:underline">
              estante
            </Link>
            .
          </p>
        )}
        {items && items.length > 0 && (
          <ul className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {items.map((item) => (
              <li key={item.book.id}>
                <BookCard book={item.book} />
                <p className="mt-1 text-xs text-ink-soft">{item.reason}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
