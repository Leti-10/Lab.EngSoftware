import { useState } from 'react'
import { kindOf } from '../lib/books'
import { uniqueAuthors } from '../lib/catalog'
import type { CatalogBook } from '../lib/types'

export function ExternalBookCard({
  book,
  busy,
  onPick,
}: {
  book: CatalogBook
  busy: boolean
  onPick: (book: CatalogBook) => void
}) {
  const [failed, setFailed] = useState(false)

  return (
    <button
      type="button"
      onClick={() => onPick(book)}
      disabled={busy}
      className="group block w-full text-left disabled:cursor-wait disabled:opacity-60"
    >
      <div
        aria-hidden="true"
        className="relative flex aspect-2/3 items-end overflow-hidden rounded-md bg-cream-300 p-3 text-ink shadow-sm transition-transform group-hover:-translate-y-1"
      >
        <span className="line-clamp-4 font-serif text-sm leading-snug font-semibold">
          {book.title}
        </span>
        {book.cover_url && !failed && (
          <img
            src={book.cover_url}
            alt=""
            loading="lazy"
            onError={() => setFailed(true)}
            className="absolute inset-0 size-full object-cover"
          />
        )}
      </div>
      <p className="mt-3 truncate text-sm font-medium text-ink">{book.title}</p>
      <p className="truncate text-xs text-ink-soft">{uniqueAuthors(book.authors).join(', ')}</p>
      <p className="mt-1 text-xs text-blue-warm-600">{kindOf(book.genres)}</p>
    </button>
  )
}
