import { ApiError, api } from './api'
import type { Book, BookPayload, CatalogBook } from './types'

export async function importBook(book: CatalogBook): Promise<Book> {
  const payload: BookPayload = {
    isbn: book.isbn,
    title: book.title,
    publisher: book.publisher || 'Não informada',
    authors: book.authors.length > 0 ? book.authors : ['Autor desconhecido'],
    genre: book.genres,
    theme: [],
  }
  try {
    return await api<Book>('/books', { method: 'POST', body: JSON.stringify(payload) })
  } catch (err) {
    if (err instanceof ApiError && err.status === 409) {
      const existing = await api<Book[]>(`/books?q=${encodeURIComponent(book.title)}`)
      const match = existing.find((other) => other.isbn === book.isbn)
      if (match) return match
    }
    throw err
  }
}
