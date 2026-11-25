import { SearchX, Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { BookCard } from '../components/BookCard'
import { ExternalBookCard } from '../components/ExternalBookCard'
import { Alert } from '../components/ui'
import { api } from '../lib/api'
import { importBook } from '../lib/catalog'
import type { Book, CatalogBook } from '../lib/types'

const FILTERS = [
  { label: 'Tudo', genre: '' },
  { label: 'Mangás', genre: 'Mangá' },
  { label: 'Quadrinhos', genre: 'Quadrinhos' },
]

export function CatalogPage() {
  const [params] = useSearchParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const [genre, setGenre] = useState(params.get('genre') ?? '')
  const [books, setBooks] = useState<Book[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [external, setExternal] = useState<CatalogBook[]>([])
  const [searching, setSearching] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importError, setImportError] = useState<string | null>(null)
  const term = query.trim()
  const searchesExternal = Boolean(user) && term.length >= 2 && !genre

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(() => {
      const search = new URLSearchParams()
      if (query.trim()) search.set('q', query.trim())
      if (genre) search.set('genre', genre)

      api<Book[]>(`/books?${search}`, { signal: controller.signal })
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

  useEffect(() => {
    if (!searchesExternal) return
    const controller = new AbortController()
    const timer = setTimeout(() => {
      setSearching(true)
      api<CatalogBook[]>(`/catalog/search?q=${encodeURIComponent(term)}`, {
        signal: controller.signal,
      })
        .then((data) => setExternal(data))
        .catch((err: Error) => {
          if (err.name !== 'AbortError') setExternal([])
        })
        .finally(() => !controller.signal.aborted && setSearching(false))
    }, 600)

    return () => {
      clearTimeout(timer)
      controller.abort()
      setSearching(false)
    }
  }, [searchesExternal, term])

  async function handlePick(book: CatalogBook) {
    setImportError(null)
    setImporting(true)
    try {
      const saved = await importBook(book)
      navigate(`/livros/${saved.id}`)
    } catch (err) {
      setImportError(err instanceof Error ? err.message : 'Não foi possível adicionar a obra.')
      setImporting(false)
    }
  }

  const known = new Set((books ?? []).flatMap((book) => [book.isbn, book.title.toLowerCase()]))
  const fromOutside = searchesExternal
    ? external.filter((book) => !known.has(book.isbn) && !known.has(book.title.toLowerCase()))
    : []
  const empty = books?.length === 0 && fromOutside.length === 0 && !searching

  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold">Estante</h1>
          <p className="mt-1 text-sm text-ink-soft">Livros, mangás e quadrinhos cadastrados.</p>
        </div>
        <div className="relative w-full sm:w-80">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute top-1/2 left-4 size-4 -translate-y-1/2 text-ink-soft"
          />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar por título ou autor"
            aria-label="Buscar por título ou autor"
            className="w-full rounded-full border border-line bg-cream-50 py-2.5 pr-5 pl-11 text-sm placeholder:text-ink-soft focus:border-blue-warm-500 focus:outline-none"
          />
        </div>
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
        {genre && !FILTERS.some((filter) => filter.genre === genre) && (
          <button
            aria-pressed="true"
            aria-label={`Remover filtro ${genre}`}
            onClick={() => setGenre('')}
            className="rounded-full border border-blue-warm-600 bg-blue-warm-600 px-4 py-1.5 text-sm text-cream-50"
          >
            {genre} ×
          </button>
        )}
      </div>

      <div className="mt-8">
        {error && <Alert>{error}</Alert>}
        {!error && books === null && <p className="text-ink-soft">Carregando…</p>}
        {importError && <Alert>{importError}</Alert>}
        {empty && (
          <p className="py-16 text-center text-ink-soft">
            <SearchX aria-hidden="true" className="mx-auto mb-3 size-8 text-blue-warm-500" />
            Nenhuma obra encontrada.{' '}
            <Link to="/livros/novo" className="font-medium text-blue-warm-600 hover:underline">
              Cadastrar uma obra
            </Link>
          </p>
        )}
        {((books && books.length > 0) || fromOutside.length > 0) && (
          <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {books?.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
            {fromOutside.map((book) => (
              <ExternalBookCard key={book.isbn} book={book} busy={importing} onPick={handlePick} />
            ))}
          </div>
        )}
        {searching && <p className="mt-6 text-sm text-ink-soft">Buscando mais obras…</p>}
      </div>
    </div>
  )
}
