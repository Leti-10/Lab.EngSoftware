import { ApiError, api } from './api'
import type { Book, BookPayload, CatalogBook } from './types'

export function uniqueAuthors(authors: string[]): string[] {
  const seen = new Set<string>()
  return authors.filter((author) => {
    const key = author.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim()
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
}

export async function importBook(book: CatalogBook): Promise<Book> {
  const payload: BookPayload = {
    isbn: book.isbn,
    title: book.title,
    publisher: book.publisher || 'Não informada',
    authors:
      uniqueAuthors(book.authors).length > 0 ? uniqueAuthors(book.authors) : ['Autor desconhecido'],
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
