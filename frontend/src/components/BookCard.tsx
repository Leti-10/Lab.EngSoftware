import { useState } from 'react'
import { Link } from 'react-router-dom'
import { kindOf } from '../lib/books'
import type { Book } from '../lib/types'

const TINTS = [
  'bg-[#cfd8e0] text-blue-warm-700',
  'bg-cream-300 text-ink',
  'bg-blue-warm-500 text-cream-50',
  'bg-cream-200 text-blue-warm-700',
]

export function coverUrl(isbn: string) {
  return `https://covers.openlibrary.org/b/isbn/${encodeURIComponent(isbn)}-M.jpg?default=false`
}

export function BookCover({ book, className = '' }: { book: Book; className?: string }) {
  const [failed, setFailed] = useState(false)

  return (
    <div
      className={`relative flex aspect-[2/3] items-end overflow-hidden rounded-md p-3 shadow-sm ${TINTS[book.id % TINTS.length]} ${className}`}
      aria-hidden="true"
    >
      <span className="line-clamp-4 font-serif text-sm leading-snug font-semibold">
        {book.title}
      </span>
      {!failed && (
        <img
          src={coverUrl(book.isbn)}
          alt=""
          loading="lazy"
          onError={() => setFailed(true)}
          className="absolute inset-0 size-full object-cover"
        />
      )}
    </div>
  )
}

export function BookCard({ book }: { book: Book }) {
  return (
    <Link to={`/livros/${book.id}`} className="group block">
      <BookCover book={book} className="transition-transform group-hover:-translate-y-1" />
      <p className="mt-3 truncate text-sm font-medium text-ink">{book.title}</p>
      <p className="truncate text-xs text-ink-soft">{book.authors.join(', ')}</p>
      <p className="mt-1 text-xs text-blue-warm-600">{kindOf(book.genre)}</p>
    </Link>
  )
}
