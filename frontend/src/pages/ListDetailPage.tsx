import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { BookCard } from '../components/BookCard'
import { Alert, Button } from '../components/ui'
import { ApiError, api } from '../lib/api'
import type { Book, BookList } from '../lib/types'

export function ListDetailPage() {
  const { id } = useParams()
  const [list, setList] = useState<BookList | null>(null)
  const [catalog, setCatalog] = useState<Book[]>([])
  const [error, setError] = useState<ApiError | null>(null)

  const [selected, setSelected] = useState('')
  const [addError, setAddError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    let cancelled = false
    Promise.all([api<BookList>(`/lists/${id}`), api<Book[]>('/books')])
      .then(([listData, books]) => {
        if (cancelled) return
        setList(listData)
        setCatalog(books)
      })
      .catch((err: ApiError) => !cancelled && setError(err))
    return () => {
      cancelled = true
    }
  }, [id])

  async function handleAdd(event: FormEvent) {
    event.preventDefault()
    if (!selected) return
    setAddError(null)
    setAdding(true)
    try {
      const updated = await api<BookList>(`/lists/${id}/books`, {
        method: 'POST',
        body: JSON.stringify({ book_id: Number(selected) }),
      })
      setList(updated)
      setSelected('')
    } catch (err) {
      setAddError(err instanceof Error ? err.message : 'Não foi possível adicionar a obra.')
    } finally {
      setAdding(false)
    }
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Alert>{error.status === 404 ? 'Lista não encontrada.' : error.message}</Alert>
        <Link to="/listas" className="text-sm font-medium text-blue-warm-600 hover:underline">
          ← Voltar para minhas listas
        </Link>
      </div>
    )
  }
  if (!list) return <p className="text-ink-soft">Carregando…</p>

  const inList = new Set(list.books.map((book) => book.id))
  const available = catalog.filter((book) => !inList.has(book.id))

  return (
    <div>
      <Link to="/listas" className="text-sm text-ink-soft hover:text-ink">
        ← Minhas listas
      </Link>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-6">
        <div>
          <h1 className="text-3xl font-semibold">{list.name}</h1>
          <p className="mt-1 text-sm text-ink-soft">
            {list.description}
            {list.private && <span className="ml-2 text-blue-warm-600">· Privada</span>}
          </p>
        </div>

        <form onSubmit={handleAdd} className="flex gap-2">
          <select
            aria-label="Escolher obra para adicionar"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            className="max-w-56 rounded-full border border-cream-300 bg-cream-50 px-4 py-2.5 text-sm text-ink focus:border-blue-warm-500 focus:outline-none"
          >
            <option value="">Adicionar obra…</option>
            {available.map((book) => (
              <option key={book.id} value={book.id}>
                {book.title}
              </option>
            ))}
          </select>
          <Button type="submit" disabled={!selected || adding}>
            Adicionar
          </Button>
        </form>
      </div>
      {addError && (
        <div className="mt-4">
          <Alert>{addError}</Alert>
        </div>
      )}

      <div className="mt-8">
        {list.books.length === 0 ? (
          <p className="py-16 text-center text-ink-soft">Esta lista ainda está vazia.</p>
        ) : (
          <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {list.books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
