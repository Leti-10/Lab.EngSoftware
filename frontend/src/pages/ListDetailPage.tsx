import { Pencil, Trash2 } from 'lucide-react'
import { useEffect, useId, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { BookCard } from '../components/BookCard'
import { FollowButton } from '../components/FollowButton'
import { Alert, Button, Field } from '../components/ui'
import { ApiError, api } from '../lib/api'
import { useDocumentTitle } from '../lib/pageTitle'
import type { Book, BookList } from '../lib/types'

export function ListDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [list, setList] = useState<BookList | null>(null)
  useDocumentTitle(list?.name)
  const [catalog, setCatalog] = useState<Book[]>([])
  const [error, setError] = useState<ApiError | null>(null)

  const [selected, setSelected] = useState('')
  const [addError, setAddError] = useState<string | null>(null)
  const [adding, setAdding] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editName, setEditName] = useState('')
  const [editDescription, setEditDescription] = useState('')
  const [editPrivate, setEditPrivate] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)
  const [savingEdit, setSavingEdit] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [deleting, setDeleting] = useState(false)
  const editDialogTitleId = useId()
  const deleteDialogTitleId = useId()

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

  function openEditDialog() {
    if (!list) return
    setEditName(list.name)
    setEditDescription(list.description)
    setEditPrivate(list.private)
    setEditError(null)
    setEditing(true)
  }

  async function handleUpdate(event: FormEvent) {
    event.preventDefault()
    const name = editName.trim()
    const description = editDescription.trim()
    if (name.length < 3) {
      setEditError('O nome deve ter pelo menos 3 caracteres.')
      return
    }
    if (!description) {
      setEditError('Escreva uma breve descrição.')
      return
    }

    setSavingEdit(true)
    setEditError(null)
    try {
      const updated = await api<BookList>(`/lists/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ name, description, private: editPrivate }),
      })
      setList(updated)
      setEditing(false)
    } catch (err) {
      setEditError(err instanceof Error ? err.message : 'Não foi possível editar a lista.')
    } finally {
      setSavingEdit(false)
    }
  }

  async function handleDelete() {
    setDeleting(true)
    setDeleteError(null)
    try {
      await api<null>(`/lists/${id}`, { method: 'DELETE' })
      navigate('/listas')
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : 'Não foi possível excluir a lista.')
    } finally {
      setDeleting(false)
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
  const isOwner = user?.id === list.owner

  return (
    <div>
      <Link
        to={isOwner ? '/listas' : `/usuarios/${list.owner}`}
        className="text-sm text-ink-soft hover:text-ink"
      >
        {isOwner ? '← Minhas listas' : '← Voltar para o perfil'}
      </Link>
      <div className="mt-4 flex flex-wrap items-end justify-between gap-6">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-3xl font-semibold">{list.name}</h1>
            {isOwner && (
              <>
                <button
                  type="button"
                  aria-label="Editar lista"
                  title="Editar lista"
                  onClick={openEditDialog}
                  className="rounded-full p-2 text-blue-warm-600 transition-colors hover:bg-blue-warm-50"
                >
                  <Pencil aria-hidden="true" className="size-4" />
                </button>
                <button
                  type="button"
                  aria-label="Excluir lista"
                  title="Excluir lista"
                  onClick={() => {
                    setDeleteError(null)
                    setConfirmingDelete(true)
                  }}
                  className="rounded-full p-2 text-danger transition-colors hover:bg-danger/10"
                >
                  <Trash2 aria-hidden="true" className="size-4" />
                </button>
              </>
            )}
          </div>
          <p className="mt-1 text-sm text-ink-soft">
            {list.description}
            {list.private && <span className="ml-2 text-blue-warm-600">· Privada</span>}
          </p>
        </div>

        {!isOwner && <FollowButton target="lists" id={list.id} />}

        {isOwner && (
          <form onSubmit={handleAdd} className="flex gap-2">
            <select
              aria-label="Escolher obra para adicionar"
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
              className="max-w-56 rounded-full border border-line bg-cream-50 px-4 py-2.5 text-sm text-ink focus:border-blue-warm-500 focus:outline-none"
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
        )}
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

      {editing && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-ink/30 px-4 backdrop-blur-sm">
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby={editDialogTitleId}
            className="w-full max-w-md rounded-2xl border border-cream-300 bg-cream-50 p-6 shadow-xl"
          >
            <h2 id={editDialogTitleId} className="text-xl font-semibold text-ink">
              Editar lista
            </h2>
            <form onSubmit={handleUpdate} noValidate className="mt-5 space-y-4">
              <Field
                label="Nome"
                value={editName}
                onChange={(event) => {
                  setEditName(event.target.value)
                  setEditError(null)
                }}
              />
              <div>
                <label
                  htmlFor={`${editDialogTitleId}-description`}
                  className="mb-1.5 block text-sm font-medium text-ink"
                >
                  Descrição
                </label>
                <textarea
                  id={`${editDialogTitleId}-description`}
                  value={editDescription}
                  onChange={(event) => {
                    setEditDescription(event.target.value)
                    setEditError(null)
                  }}
                  rows={3}
                  className="w-full resize-y rounded-xl border border-line bg-cream-50 px-4 py-2.5 text-sm text-ink focus:border-blue-warm-500 focus:outline-none"
                />
              </div>
              <label className="flex items-center gap-2 text-sm text-ink-soft">
                <input
                  type="checkbox"
                  checked={editPrivate}
                  onChange={(event) => setEditPrivate(event.target.checked)}
                  className="size-4 accent-blue-warm-600"
                />
                Lista privada
              </label>
              {editError && <Alert>{editError}</Alert>}
              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setEditing(false)}
                  disabled={savingEdit}
                >
                  Cancelar
                </Button>
                <Button type="submit" disabled={savingEdit}>
                  {savingEdit ? 'Salvando…' : 'Salvar alterações'}
                </Button>
              </div>
            </form>
          </section>
        </div>
      )}

      {confirmingDelete && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-ink/30 px-4 backdrop-blur-sm">
          <section
            role="alertdialog"
            aria-modal="true"
            aria-labelledby={deleteDialogTitleId}
            className="w-full max-w-md rounded-2xl border border-cream-300 bg-cream-50 p-6 shadow-xl"
          >
            <h2 id={deleteDialogTitleId} className="text-xl font-semibold text-ink">
              Excluir lista?
            </h2>
            <p className="mt-2 text-sm text-ink-soft">
              Excluir <strong className="text-ink">{list.name}</strong>? Esta ação não pode ser
              desfeita.
            </p>
            {deleteError && (
              <div className="mt-4">
                <Alert>{deleteError}</Alert>
              </div>
            )}
            <div className="mt-5 flex justify-end gap-2">
              <Button
                type="button"
                variant="ghost"
                onClick={() => setConfirmingDelete(false)}
                disabled={deleting}
              >
                Cancelar
              </Button>
              <button
                type="button"
                onClick={handleDelete}
                disabled={deleting}
                className="rounded-full bg-danger px-5 py-2.5 text-sm font-medium text-cream-50 transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {deleting ? 'Excluindo…' : 'Confirmar exclusão'}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  )
}
