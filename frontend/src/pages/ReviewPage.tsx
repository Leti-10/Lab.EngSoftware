import { Heart } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Alert } from '../components/ui'
import { api } from '../lib/api'
import { coverUrl } from '../components/BookCard'
import { useDocumentTitle } from '../lib/pageTitle'
import type { ReviewFeedItem, ReviewFeedPage } from '../lib/types'

type ReviewSort = 'recent' | 'popular'

function formatReviewDate(value: ReviewFeedItem['created_at']) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Data indisponível'
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function ReviewCover({ item }: { item: ReviewFeedItem }) {
  const [failed, setFailed] = useState(false)
  const title = item.book_title ?? 'Obra não encontrada'

  return (
    <div className="relative aspect-2/3 w-20 shrink-0 overflow-hidden rounded-lg bg-cream-300 shadow-sm sm:w-24">
      {item.book_isbn && !failed ? (
        <img
          src={coverUrl(item.book_isbn)}
          alt={`Capa de ${title}`}
          loading="lazy"
          onError={() => setFailed(true)}
          className="absolute inset-0 size-full object-cover"
        />
      ) : (
        <div className="flex size-full items-end p-2 text-xs font-semibold text-ink">{title}</div>
      )}
    </div>
  )
}

function ReviewRow({ item, index }: { item: ReviewFeedItem; index: number }) {
  const bookTitle = item.book_title ?? 'obra'
  const author = item.username ?? 'Leitor'
  const date = new Date(item.created_at)
  const dateTime = Number.isNaN(date.getTime()) ? undefined : date.toISOString()

  return (
    <li>
      <Link
        to={`/livros/${item.book_id}`}
        aria-label={`Resenha de ${author} sobre ${bookTitle}`}
        className={`group flex items-start gap-4 rounded-2xl border border-line bg-cream-50 p-4 shadow-sm transition-colors hover:bg-cream-200 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-warm-600 sm:gap-6 sm:p-5 ${
          index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'
        }`}
      >
        <ReviewCover item={item} />
        <div className="min-w-0 flex-1 self-center">
          <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
            <span className="font-semibold text-ink">{author}</span>
            <time dateTime={dateTime} className="text-xs text-ink-soft">
              {formatReviewDate(item.created_at)}
            </time>
          </div>
          <p className="mt-2 line-clamp-5 whitespace-pre-line text-sm leading-relaxed text-ink">
            {item.comment?.trim() || 'Esta resenha não contém texto.'}
          </p>
          <span className="mt-3 inline-flex items-center gap-1.5 text-xs text-ink-soft">
            <Heart aria-hidden="true" className="size-4" />
            {item.likes} {item.likes === 1 ? 'curtida' : 'curtidas'}
          </span>
        </div>
      </Link>
    </li>
  )
}

export default function ReviewPage() {
  useDocumentTitle('Resenhas')
  const [sort, setSort] = useState<ReviewSort>('recent')
  const [page, setPage] = useState(1)
  const [result, setResult] = useState<{
    key: string
    data: ReviewFeedPage
  } | null>(null)
  const [failure, setFailure] = useState<{ key: string; message: string } | null>(null)
  const requestKey = `${sort}:${page}`

  useEffect(() => {
    let cancelled = false
    const query = new URLSearchParams({ page: String(page), sort })

    api<ReviewFeedPage>(`/reviews/feed?${query}`)
      .then((result) => {
        if (!cancelled) {
          setResult({ key: requestKey, data: result })
          setFailure(null)
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setFailure({ key: requestKey, message: err.message })
      })

    return () => {
      cancelled = true
    }
  }, [page, requestKey, sort])

  function changeSort(value: ReviewSort) {
    setSort(value)
    setPage(1)
  }

  const data = result?.key === requestKey ? result.data : null
  const error = failure?.key === requestKey ? failure.message : null
  const loading = data === null && error === null
  const pageCount = data ? Math.ceil(data.total / data.page_size) : 0

  return (
    <section className="mx-auto max-w-4xl">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Resenhas</h1>
          <p className="mt-1 text-sm text-ink-soft">
            Leia as opiniões da comunidade sobre suas obras favoritas.
          </p>
        </div>
        <label className="flex flex-col gap-1.5 text-sm font-medium text-ink">
          Ordenar resenhas
          <select
            value={sort}
            onChange={(event) => {
              const value = event.target.value
              if (value === 'recent' || value === 'popular') changeSort(value)
            }}
            className="min-h-11 rounded-xl border border-line bg-cream-50 px-3 text-sm focus:border-blue-warm-500 focus:outline-none"
          >
            <option value="recent">Mais recentes</option>
            <option value="popular">Mais curtidas</option>
          </select>
        </label>
      </div>

      <div className="mt-6">
        {error && <Alert>{error}</Alert>}
        {loading && <p className="py-8 text-center text-ink-soft">Carregando resenhas…</p>}
        {!loading && data?.items.length === 0 && (
          <p className="py-12 text-center text-ink-soft">Nenhuma resenha foi publicada ainda.</p>
        )}
        {data && data.items.length > 0 && (
          <ul aria-label="Resenhas da comunidade" className="space-y-4">
            {data.items.map((item, index) => (
              <ReviewRow key={item.id} item={item} index={index} />
            ))}
          </ul>
        )}
      </div>

      {data && pageCount > 1 && (
        <nav
          aria-label="Paginação das resenhas"
          className="mt-8 flex flex-wrap justify-center gap-2"
        >
          {Array.from({ length: pageCount }, (_, index) => index + 1).map((pageNumber) => (
            <button
              key={pageNumber}
              type="button"
              aria-label={`Página ${pageNumber}`}
              aria-current={pageNumber === page ? 'page' : undefined}
              disabled={pageNumber === page || loading}
              onClick={() => setPage(pageNumber)}
              className="min-h-10 min-w-10 rounded-full border border-line px-3 text-sm text-ink transition-colors hover:bg-cream-200 disabled:border-blue-warm-600 disabled:bg-blue-warm-600 disabled:text-cream-50"
            >
              {pageNumber}
            </button>
          ))}
        </nav>
      )}
    </section>
  )
}
