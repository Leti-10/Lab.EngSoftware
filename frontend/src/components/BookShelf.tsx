import { ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Book } from '../lib/types'
import { BookCard } from './BookCard'

interface BookShelfProps {
  title: string
  books: Book[]
  moreTo?: string
}

export function BookShelf({ title, books, moreTo }: BookShelfProps) {
  if (books.length === 0) return null

  return (
    <section className="rounded-2xl bg-cream-200/60 p-5">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">
          {title} <span className="text-ink-soft">({books.length})</span>
        </h2>
        {moreTo && (
          <Link
            to={moreTo}
            className="flex items-center gap-1 text-sm font-medium text-blue-warm-600 hover:underline"
          >
            Ver mais
            <ChevronRight aria-hidden="true" className="size-4" />
          </Link>
        )}
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4 sm:grid-cols-4 md:grid-cols-6">
        {books.slice(0, 6).map((book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>
    </section>
  )
}
