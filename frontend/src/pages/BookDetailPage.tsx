import { ArrowLeft, Barcode, Building2, Layers, PenLine, Pencil, Trash2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { BookCover } from '../components/BookCard'
import { BookShelf } from '../components/BookShelf'
import { FavoriteButton } from '../components/FavoriteButton'
import { ReadingStatus } from '../components/ReadingStatus'
import { ReviewSection } from '../components/ReviewSection'
import { Stars } from '../components/StarRating'
import { Alert, Button } from '../components/ui'
import { ApiError, api } from '../lib/api'
import { kindOf } from '../lib/books'
import { useDocumentTitle } from '../lib/pageTitle'
import { averageOf } from '../lib/reviews'
import type { Book, Review } from '../lib/types'

const TABS = ['Detalhes', 'Gêneros', 'Temas'] as const
type Tab = (typeof TABS)[number]

function MetaPill({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full bg-cream-200/70 px-3 py-1.5 text-xs text-ink">
      {icon}
      {children}
    </span>
  )
}

function Chip({ children, to }: { children: string; to?: string }) {
  const className = 'rounded-full bg-blue-warm-50 px-3 py-1.5 text-sm text-blue-warm-700'
  if (!to) return <span className={className}>{children}</span>
  return (
    <Link to={to} className={`${className} transition-colors hover:bg-blue-warm-100`}>
      {children}
    </Link>
  )
}

export function BookDetailPage() {
  const { id } = useParams()

  return <BookDetail key={id} id={id} />
}

function BookDetail({ id }: { id?: string }) {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [book, setBook] = useState<Book | null>(null)
  useDocumentTitle(book?.title)
  const [error, setError] = useState<ApiError | null>(null)
  const [tab, setTab] = useState<Tab>('Detalhes')
  const [sameAuthor, setSameAuthor] = useState<Book[]>([])
  const [similar, setSimilar] = useState<Book[]>([])
  const [reviews, setReviews] = useState<Review[]>([])
  const [confirming, setConfirming] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api<Book>(`/books/${id}`)
      .then((data) => !cancelled && setBook(data))
      .catch((err: ApiError) => !cancelled && setError(err))
    return () => {
      cancelled = true
    }
  }, [id])

  useEffect(() => {
    if (!book) return
    let cancelled = false
    const others = (books: Book[]) => books.filter((other) => other.id !== book.id)
    const firstGenre = book.genre.find((genre) => genre !== kindOf(book.genre))

    api<Review[]>(`/reviews?book_id=${book.id}`)
      .then((data) => !cancelled && setReviews(data))
      .catch(() => undefined)
    api<Book[]>(`/books?q=${encodeURIComponent(book.authors[0])}`)
      .then((data) => !cancelled && setSameAuthor(others(data)))
      .catch(() => undefined)
    if (firstGenre) {
      api<Book[]>(`/books?genre=${encodeURIComponent(firstGenre)}`)
        .then((data) => !cancelled && setSimilar(others(data)))
        .catch(() => undefined)
    }

    return () => {
      cancelled = true
    }
  }, [book])

  async function handleDelete() {
    setDeleteError(null)
    setDeleting(true)
    try {
      await api(`/books/${id}`, { method: 'DELETE' })
      navigate('/livros')
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Não foi possível excluir a obra.')
      setDeleting(false)
    }
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert>{error.status === 404 ? 'Obra não encontrada.' : error.message}</Alert>
        <Link
          to="/livros"
          className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-warm-600 hover:underline"
        >
          <ArrowLeft aria-hidden="true" className="size-4" />
          Voltar para a estante
        </Link>
      </div>
    )
  }
  if (!book) return <p className="text-ink-soft">Carregando…</p>

  const kind = kindOf(book.genre)
  const genres = book.genre.filter((genre) => genre !== kind)
  const authorName = book.authors[0]
  const average = averageOf(reviews.map((review) => review.rating))

  return (
    <div>
      <Link
        to="/livros"
        className="inline-flex items-center gap-1.5 text-sm text-ink-soft hover:text-ink"
      >
        <ArrowLeft aria-hidden="true" className="size-4" />
        Estante
      </Link>

      <div className="mt-6 grid gap-8 md:grid-cols-[200px_1fr] lg:grid-cols-[200px_1fr_250px]">
        <div className="mx-auto w-full max-w-50 md:mx-0">
          <BookCover book={book} className="w-full" />
          <p className="mt-3 text-center text-xs text-ink-soft">{kind}</p>
        </div>

        <div className="min-w-0">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h1 className="text-3xl font-semibold sm:text-4xl">{book.title}</h1>
          </div>
          <p className="mt-2 text-ink-soft">
            por{' '}
            {book.authors.map((author, index) => (
              <span key={author}>
                {index > 0 && ', '}
                <Link
                  to={`/livros?q=${encodeURIComponent(author)}`}
                  className="font-medium text-ink underline decoration-blue-warm-100 underline-offset-4 hover:decoration-blue-warm-500"
                >
                  {author}
                </Link>
              </span>
            ))}
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <MetaPill icon={<Building2 aria-hidden="true" className="size-3.5 text-ink-soft" />}>
              {book.publisher}
            </MetaPill>
            <MetaPill icon={<Barcode aria-hidden="true" className="size-3.5 text-ink-soft" />}>
              ISBN-13: {book.isbn}
            </MetaPill>
            <MetaPill icon={<Layers aria-hidden="true" className="size-3.5 text-ink-soft" />}>
              {kind}
            </MetaPill>
          </div>

          {user && (
            <div className="mt-5 flex flex-wrap items-center gap-2">
              <FavoriteButton book={book} />
              <Link to={`/livros/${book.id}/editar`}>
                <Button variant="ghost" className="gap-2">
                  <Pencil aria-hidden="true" className="size-4" />
                  Editar
                </Button>
              </Link>
              {!confirming && (
                <Button variant="ghost" className="gap-2" onClick={() => setConfirming(true)}>
                  <Trash2 aria-hidden="true" className="size-4" />
                  Excluir
                </Button>
              )}
            </div>
          )}

          {confirming && (
            <div
              role="alertdialog"
              aria-label="Confirmar exclusão"
              className="mt-4 rounded-2xl border border-danger/30 bg-danger/5 p-4"
            >
              <p className="text-sm text-ink">
                Excluir <strong>{book.title}</strong>? Essa ação não pode ser desfeita.
              </p>
              <div className="mt-3 flex gap-2">
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleting}
                  className="rounded-full bg-danger px-5 py-2 text-sm font-medium text-cream-50 transition-opacity hover:opacity-90 disabled:opacity-60"
                >
                  {deleting ? 'Excluindo…' : 'Confirmar exclusão'}
                </button>
                <Button variant="ghost" onClick={() => setConfirming(false)} disabled={deleting}>
                  Cancelar
                </Button>
              </div>
              {deleteError && (
                <div className="mt-3">
                  <Alert>{deleteError}</Alert>
                </div>
              )}
            </div>
          )}
          <div className="mt-8">
            <div
              role="tablist"
              aria-label="Informações da obra"
              className="flex gap-6 border-b border-cream-300"
            >
              {TABS.map((name) => (
                <button
                  key={name}
                  role="tab"
                  type="button"
                  aria-selected={tab === name}
                  onClick={() => setTab(name)}
                  className={`-mb-px border-b-2 pb-2 text-xs font-semibold tracking-widest uppercase transition-colors ${
                    tab === name
                      ? 'border-blue-warm-600 text-ink'
                      : 'border-transparent text-blue-warm-600 hover:text-blue-warm-700'
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>

            <div role="tabpanel" className="pt-5">
              {tab === 'Detalhes' && (
                <dl className="grid grid-cols-[110px_1fr] gap-y-3 text-sm">
                  <dt className="text-ink-soft">Tipo</dt>
                  <dd>{kind}</dd>
                  <dt className="text-ink-soft">Autores</dt>
                  <dd>{book.authors.join(', ')}</dd>
                  <dt className="text-ink-soft">Editora</dt>
                  <dd>{book.publisher}</dd>
                  <dt className="text-ink-soft">ISBN</dt>
                  <dd>{book.isbn}</dd>
                </dl>
              )}
              {tab === 'Gêneros' &&
                (genres.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {genres.map((genre) => (
                      <Chip key={genre} to={`/livros?genre=${encodeURIComponent(genre)}`}>
                        {genre}
                      </Chip>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-ink-soft">Nenhum gênero informado.</p>
                ))}
              {tab === 'Temas' &&
                (book.theme.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {book.theme.map((theme) => (
                      <Chip key={theme}>{theme}</Chip>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-ink-soft">Nenhum tema informado.</p>
                ))}
            </div>
          </div>
        </div>

        <aside
          aria-label="Ações da obra"
          className="h-fit overflow-hidden rounded-2xl border border-cream-300 bg-cream-50 md:col-span-2 lg:col-span-1"
        >
          <ReadingStatus bookId={book.id} />
          <div className="border-t border-cream-300">
            <a
              href="#resenhas"
              className="flex flex-col items-center gap-2 px-2 py-4 text-xs text-ink transition-colors hover:bg-cream-200"
            >
              <PenLine aria-hidden="true" className="size-6" />
              Resenhar
            </a>
          </div>

          <div className="border-t border-cream-300 px-4 py-4 text-center">
            <p className="text-xs text-ink-soft">Avaliação</p>
            {reviews.length > 0 ? (
              <>
                <p className="mt-1 text-3xl font-semibold text-ink">
                  {average.toFixed(1).replace('.', ',')}
                </p>
                <div className="mt-1 flex justify-center">
                  <Stars value={average} size="size-5" />
                </div>
                <p className="mt-2 text-xs text-ink-soft">
                  {reviews.length} {reviews.length === 1 ? 'avaliação' : 'avaliações'}
                </p>
              </>
            ) : (
              <p className="mt-3 text-xs text-ink-soft">Ainda sem avaliações</p>
            )}
          </div>
        </aside>
      </div>

      <ReviewSection bookId={book.id} reviews={reviews} onChange={setReviews} />

      <div className="mt-12 space-y-6">
        <BookShelf
          title={`Mais de ${authorName}`}
          books={sameAuthor}
          moreTo={`/livros?q=${encodeURIComponent(authorName)}`}
        />
        <BookShelf
          title="Obras parecidas"
          books={similar}
          moreTo={genres[0] ? `/livros?genre=${encodeURIComponent(genres[0])}` : undefined}
        />
      </div>
    </div>
  )
}
