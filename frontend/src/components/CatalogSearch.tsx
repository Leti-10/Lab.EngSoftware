import { Search } from 'lucide-react'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../lib/api'
import type { CatalogBook } from '../lib/types'
import { Alert, Button, Card } from './ui'

function Thumbnail({ book }: { book: CatalogBook }) {
  const [failed, setFailed] = useState(false)

  if (!book.cover_url || failed) {
    return (
      <span
        aria-hidden="true"
        className="grid h-20 w-14 shrink-0 place-items-center rounded-md bg-cream-300 font-serif text-lg text-ink-soft"
      >
        {book.title.charAt(0)}
      </span>
    )
  }

  return (
    <img
      src={book.cover_url}
      alt=""
      loading="lazy"
      onError={() => setFailed(true)}
      className="h-20 w-14 shrink-0 rounded-md object-cover shadow-sm"
    />
  )
}

export function CatalogSearch({ onPick }: { onPick: (book: CatalogBook) => void }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<CatalogBook[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [picked, setPicked] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setPicked(null)

    if (query.trim().length < 2) {
      setError('Digite ao menos 2 caracteres para buscar.')
      setResults(null)
      return
    }

    setError(null)
    setLoading(true)
    try {
      const data = await api<CatalogBook[]>(`/catalog/search?q=${encodeURIComponent(query.trim())}`)
      setResults(data)
    } catch (err) {
      setResults(null)
      setError(err instanceof Error ? err.message : 'Não foi possível buscar agora.')
    } finally {
      setLoading(false)
    }
  }

  function handlePick(book: CatalogBook) {
    onPick(book)
    setPicked(book.title)
    setResults(null)
  }

  return (
    <Card className="mt-8">
      <h2 className="text-lg font-semibold">Buscar livro</h2>
      <p className="mt-1 text-sm text-ink-soft">
        Procure pelo título, autor ou ISBN para preencher os dados automaticamente.
      </p>

      <form onSubmit={handleSubmit} noValidate role="search" className="mt-4 flex gap-2">
        <div className="relative flex-1">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute top-1/2 left-4 size-4 -translate-y-1/2 text-ink-soft"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ex.: Dom Casmurro"
            aria-label="Buscar livro por título, autor ou ISBN"
            className="w-full rounded-full border border-cream-300 bg-cream-50 py-2.5 pr-4 pl-11 text-sm placeholder:text-ink-soft/60 focus:border-blue-warm-500 focus:outline-none"
          />
        </div>
        <Button type="submit" disabled={loading}>
          {loading ? 'Buscando…' : 'Buscar'}
        </Button>
      </form>

      {error && (
        <div className="mt-4">
          <Alert>{error}</Alert>
        </div>
      )}

      {picked && (
        <p
          role="status"
          className="mt-4 rounded-xl bg-blue-warm-50 px-4 py-2.5 text-sm text-blue-warm-700"
        >
          Dados de “{picked}” preenchidos. Revise antes de cadastrar.
        </p>
      )}

      {results?.length === 0 && (
        <p className="mt-4 text-sm text-ink-soft">
          Nenhum livro encontrado. Você pode preencher os dados manualmente.
        </p>
      )}

      {results && results.length > 0 && (
        <ul aria-label="Resultados da busca" className="mt-4 divide-y divide-cream-300">
          {results.map((book) => (
            <li key={book.isbn} className="flex items-center gap-4 py-3">
              <Thumbnail book={book} />
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{book.title}</p>
                <p className="truncate text-xs text-ink-soft">
                  {book.authors.join(', ') || 'Autor não informado'}
                </p>
                <p className="truncate text-xs text-ink-soft">
                  {[book.publisher, `ISBN ${book.isbn}`].filter(Boolean).join(' · ')}
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                aria-label={`Usar ${book.title}`}
                onClick={() => handlePick(book)}
              >
                Usar
              </Button>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
