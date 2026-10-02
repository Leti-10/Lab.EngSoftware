import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BookCard } from '../components/BookCard'
import { Alert } from '../components/ui'
import { api } from '../lib/api'
import type { Book } from '../lib/types'

const FILTERS = [
  { label: 'Tudo', genre: '' },
  { label: 'Mangás', genre: 'Mangá' },
  { label: 'Quadrinhos', genre: 'Quadrinhos' },
]

export function CatalogPage() {
  const [query, setQuery] = useState('')
  const [genre, setGenre] = useState('')
  const [books, setBooks] = useState<Book[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(() => {
      const params = new URLSearchParams()
      if (query.trim()) params.set('q', query.trim())
      if (genre) params.set('genre', genre)

      api<Book[]>(`/books?${params}`, { signal: controller.signal })
        .then((data) => {
          setBooks(data)
          setError(null)
        })
        .catch((err: Error) => {
          if (err.name !== 'AbortError') setError(err.message)
        })
    }, 250)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [query, genre])

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold">Estante</h1>
          <p className="mt-1 text-sm text-ink-soft">Livros, mangás e quadrinhos cadastrados.</p>
        </div>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Buscar por título ou autor"
          aria-label="Buscar por título ou autor"
          className="w-full rounded-full border border-cream-300 bg-cream-50 px-5 py-2.5 text-sm placeholder:text-ink-soft/60 focus:border-blue-warm-500 focus:outline-none sm:w-72"
        />
      </div>

      <div className="mt-6 flex gap-2">
        {FILTERS.map((filter) => (
          <button
            key={filter.label}
            aria-pressed={genre === filter.genre}
            onClick={() => setGenre(filter.genre)}
            className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
              genre === filter.genre
                ? 'border-blue-warm-600 bg-blue-warm-600 text-cream-50'
                : 'border-cream-300 text-ink-soft hover:bg-cream-200'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      <div className="mt-8">
        {error && <Alert>{error}</Alert>}
        {!error && books === null && <p className="text-ink-soft">Carregando…</p>}
        {books?.length === 0 && (
          <p className="py-16 text-center text-ink-soft">
            Nenhuma obra encontrada.{' '}
            <Link to="/livros/novo" className="font-medium text-blue-warm-600 hover:underline">
              Cadastrar uma obra
            </Link>
          </p>
        )}
        {books && books.length > 0 && (
          <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
