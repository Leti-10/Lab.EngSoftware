import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../lib/api'
import { KINDS, kindOf, splitList } from '../lib/books'
import type { Kind } from '../lib/books'
import type { Book, BookPayload } from '../lib/types'
import { Alert, Button, Card, Field } from '../components/ui'
import { compact, hasErrors } from '../lib/validation'
import type { FieldErrors } from '../lib/validation'

const emptyForm = { title: '', authors: '', isbn: '', publisher: '', genres: '', themes: '' }

type BookField = keyof typeof emptyForm

export function BookFormPage() {
  const { id } = useParams()
  const editing = id !== undefined
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [kind, setKind] = useState<Kind>('Livro')
  const [errors, setErrors] = useState<FieldErrors<BookField>>({})
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(editing)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!editing) return
    let cancelled = false

    api<Book>(`/books/${id}`)
      .then((book) => {
        if (cancelled) return
        const type = kindOf(book.genre)
        setKind(type)
        setForm({
          title: book.title,
          authors: book.authors.join(', '),
          isbn: book.isbn,
          publisher: book.publisher,
          genres: book.genre.filter((genre) => genre !== type).join(', '),
          themes: book.theme.join(', '),
        })
      })
      .catch((err: Error) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false))

    return () => {
      cancelled = true
    }
  }, [editing, id])

  const set = (field: BookField) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((current) => ({ ...current, [field]: e.target.value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  function validate() {
    let isbnError: string | undefined
    if (!form.isbn.trim()) isbnError = 'Informe o ISBN.'
    else if (form.isbn.trim().length < 10) isbnError = 'O ISBN deve ter pelo menos 10 caracteres.'

    return compact<BookField>({
      title: form.title.trim() ? undefined : 'Informe o título da obra.',
      authors: splitList(form.authors).length ? undefined : 'Informe ao menos um autor.',
      isbn: isbnError,
      publisher: form.publisher.trim() ? undefined : 'Informe a editora.',
      genres: splitList(form.genres).length ? undefined : 'Informe ao menos um gênero.',
      themes: undefined,
    })
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    const found = validate()
    setErrors(found)
    if (hasErrors(found)) return

    const payload: BookPayload = {
      isbn: form.isbn.trim(),
      title: form.title.trim(),
      publisher: form.publisher.trim(),
      authors: splitList(form.authors),
      genre: [...(kind === 'Livro' ? [] : [kind]), ...splitList(form.genres)],
      theme: splitList(form.themes),
    }

    setSubmitting(true)
    try {
      const book = await api<Book>(editing ? `/books/${id}` : '/books', {
        method: editing ? 'PUT' : 'POST',
        body: JSON.stringify(payload),
      })
      navigate(`/livros/${book.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível salvar a obra.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <p className="text-ink-soft">Carregando…</p>

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="text-3xl font-semibold">{editing ? 'Editar obra' : 'Cadastrar obra'}</h1>
      <p className="mt-2 text-sm text-ink-soft">
        {editing
          ? 'Atualize os dados da obra.'
          : 'Não achou na estante? Adicione um livro, mangá ou quadrinho.'}
      </p>

      <Card className="mt-8">
        <form onSubmit={handleSubmit} noValidate className="space-y-5">
          <fieldset>
            <legend className="mb-1.5 text-sm font-medium">Tipo</legend>
            <div className="flex gap-2">
              {KINDS.map((option) => (
                <button
                  type="button"
                  key={option}
                  aria-pressed={kind === option}
                  onClick={() => setKind(option)}
                  className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                    kind === option
                      ? 'border-blue-warm-600 bg-blue-warm-600 text-cream-50'
                      : 'border-cream-300 text-ink-soft hover:bg-cream-200'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </fieldset>

          <Field
            label="Título"
            value={form.title}
            onChange={set('title')}
            placeholder="Ex.: One Piece, Vol. 1"
            error={errors.title}
          />
          <Field
            label="Autores"
            placeholder="Ex.: Eiichiro Oda"
            error={errors.authors}
            value={form.authors}
            onChange={set('authors')}
            hint="Separe por vírgula. Ex.: Eiichiro Oda, Masashi Kishimoto"
          />
          <div className="grid gap-5 sm:grid-cols-2">
            <Field
              label="ISBN"
              placeholder="Ex.: 9788542603835"
              error={errors.isbn}
              value={form.isbn}
              onChange={set('isbn')}
              hint="Mínimo de 10 dígitos."
            />
            <Field
              label="Editora"
              value={form.publisher}
              onChange={set('publisher')}
              placeholder="Ex.: Panini"
              error={errors.publisher}
            />
          </div>
          <Field
            label="Gêneros"
            placeholder="Ex.: Aventura, Shounen"
            error={errors.genres}
            value={form.genres}
            onChange={set('genres')}
            hint="Separe por vírgula. Ex.: Aventura, Fantasia"
          />
          <Field
            label="Temas (opcional)"
            placeholder="Ex.: Amizade, Piratas"
            value={form.themes}
            onChange={set('themes')}
            hint="Separe por vírgula."
          />

          {error && <Alert>{error}</Alert>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Salvando…' : editing ? 'Salvar alterações' : 'Cadastrar'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
