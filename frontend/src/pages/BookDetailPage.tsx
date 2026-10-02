import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BookCover } from '../components/BookCard'
import { Alert } from '../components/ui'
import { ApiError, api } from '../lib/api'
import { kindOf } from '../lib/books'
import type { Book } from '../lib/types'

function Chip({ children }: { children: string }) {
  return (
    <span className="rounded-full bg-blue-warm-50 px-3 py-1 text-xs text-blue-warm-700">
      {children}
    </span>
  )
}

export function BookDetailPage() {
  const { id } = useParams()
  const [book, setBook] = useState<Book | null>(null)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let cancelled = false
    api<Book>(`/books/${id}`)
      .then((data) => !cancelled && setBook(data))
      .catch((err: ApiError) => !cancelled && setError(err))
    return () => {
      cancelled = true
    }
  }, [id])

  if (error) {
    return (
      <div className="space-y-4">
        <Alert>{error.status === 404 ? 'Obra não encontrada.' : error.message}</Alert>
        <Link to="/livros" className="text-sm font-medium text-blue-warm-600 hover:underline">
          ← Voltar para a estante
        </Link>
      </div>
    )
  }
  if (!book) return <p className="text-ink-soft">Carregando…</p>

  const genres = book.genre.filter((g) => g !== kindOf(book.genre))

  return (
    <div>
      <Link to="/livros" className="text-sm text-ink-soft hover:text-ink">
        ← Estante
      </Link>

      <div className="mt-6 grid gap-8 sm:grid-cols-[220px_1fr]">
        <BookCover book={book} className="w-full max-w-[220px]" />

        <div>
          <p className="text-sm font-medium text-blue-warm-600">{kindOf(book.genre)}</p>
          <h1 className="mt-1 text-3xl font-semibold sm:text-4xl">{book.title}</h1>
          <p className="mt-2 text-ink-soft">por {book.authors.join(', ')}</p>

          <dl className="mt-8 grid grid-cols-[110px_1fr] gap-y-3 text-sm">
            <dt className="text-ink-soft">Editora</dt>
            <dd>{book.publisher}</dd>
            <dt className="text-ink-soft">ISBN</dt>
            <dd>{book.isbn}</dd>
          </dl>

          {genres.length > 0 && (
            <section className="mt-8">
              <h2 className="text-sm font-medium text-ink-soft">Gêneros</h2>
              <div className="mt-2 flex flex-wrap gap-2">
                {genres.map((genre) => (
                  <Chip key={genre}>{genre}</Chip>
                ))}
              </div>
            </section>
          )}

          {book.theme.length > 0 && (
            <section className="mt-6">
              <h2 className="text-sm font-medium text-ink-soft">Temas</h2>
              <div className="mt-2 flex flex-wrap gap-2">
                {book.theme.map((theme) => (
                  <Chip key={theme}>{theme}</Chip>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
