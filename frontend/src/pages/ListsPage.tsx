import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Alert, Button, Card, Field } from '../components/ui'
import { compact, hasErrors } from '../lib/validation'
import type { FieldErrors } from '../lib/validation'
import { api } from '../lib/api'
import type { BookList } from '../lib/types'

export function ListsPage() {
  const [lists, setLists] = useState<BookList[] | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [isPrivate, setIsPrivate] = useState(false)
  const [errors, setErrors] = useState<FieldErrors<'name' | 'description'>>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api<BookList[]>('/lists')
      .then(setLists)
      .catch((err: Error) => setLoadError(err.message))
  }, [])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setFormError(null)

    let nameError: string | undefined
    if (!name.trim()) nameError = 'Dê um nome à lista.'
    else if (name.trim().length < 3) nameError = 'O nome deve ter pelo menos 3 caracteres.'

    const found = compact<'name' | 'description'>({
      name: nameError,
      description: description.trim() ? undefined : 'Escreva uma breve descrição.',
    })
    setErrors(found)
    if (hasErrors(found)) return

    setSubmitting(true)
    try {
      const created = await api<BookList>('/lists', {
        method: 'POST',
        body: JSON.stringify({ name, description, private: isPrivate }),
      })
      setLists((current) => [...(current ?? []), created])
      setName('')
      setDescription('')
      setIsPrivate(false)
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Não foi possível criar a lista.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="grid gap-10 md:grid-cols-[1fr_320px]">
      <section>
        <h1 className="text-3xl font-semibold">Minhas listas</h1>
        <p className="mt-1 text-sm text-ink-soft">Agrupe suas leituras do jeito que quiser.</p>

        <div className="mt-6 space-y-3">
          {loadError && <Alert>{loadError}</Alert>}
          {!loadError && lists === null && <p className="text-ink-soft">Carregando…</p>}
          {lists?.length === 0 && (
            <p className="py-10 text-ink-soft">Você ainda não criou nenhuma lista.</p>
          )}
          {lists?.map((list) => (
            <Link key={list.id} to={`/listas/${list.id}`} className="block">
              <Card className="transition-colors hover:border-blue-warm-100 hover:bg-blue-warm-50/40">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <h2 className="truncate text-lg font-semibold">{list.name}</h2>
                    <p className="mt-1 line-clamp-2 text-sm text-ink-soft">{list.description}</p>
                  </div>
                  <div className="shrink-0 text-right text-xs text-ink-soft">
                    <p>
                      {list.books.length} {list.books.length === 1 ? 'obra' : 'obras'}
                    </p>
                    {list.private && <p className="mt-1 text-blue-warm-600">Privada</p>}
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      <aside>
        <Card>
          <h2 className="text-lg font-semibold">Nova lista</h2>
          <form onSubmit={handleSubmit} noValidate className="mt-4 space-y-4">
            <Field
              label="Nome"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                setErrors((current) => ({ ...current, name: undefined }))
              }}
              placeholder="Ex.: Para ler nas férias"
              error={errors.name}
            />
            <Field
              label="Descrição"
              value={description}
              onChange={(e) => {
                setDescription(e.target.value)
                setErrors((current) => ({ ...current, description: undefined }))
              }}
              placeholder="Ex.: Mangás e HQs para o recesso"
              error={errors.description}
            />
            <label className="flex items-center gap-2 text-sm text-ink-soft">
              <input
                type="checkbox"
                checked={isPrivate}
                onChange={(e) => setIsPrivate(e.target.checked)}
                className="size-4 accent-blue-warm-600"
              />
              Lista privada
            </label>
            {formError && <Alert>{formError}</Alert>}
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? 'Criando…' : 'Criar lista'}
            </Button>
          </form>
        </Card>
      </aside>
    </div>
  )
}
