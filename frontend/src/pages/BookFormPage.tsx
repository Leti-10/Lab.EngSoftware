import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import { KINDS, splitList } from '../lib/books'
import type { Kind } from '../lib/books'
import type { Book, BookPayload } from '../lib/types'
import { Alert, Button, Card, Field } from '../components/ui'

const emptyForm = { title: '', authors: '', isbn: '', publisher: '', genres: '', themes: '' }

export function BookFormPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState(emptyForm)
  const [kind, setKind] = useState<Kind>('Livro')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const set = (field: keyof typeof emptyForm) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((current) => ({ ...current, [field]: e.target.value }))

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

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
      const book = await api<Book>('/books', { method: 'POST', body: JSON.stringify(payload) })
      navigate(`/livros/${book.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível cadastrar o livro.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="text-3xl font-semibold">Cadastrar obra</h1>
      <p className="mt-2 text-sm text-ink-soft">
        Não achou na estante? Adicione um livro, mangá ou quadrinho.
      </p>

      <Card className="mt-8">
        <form onSubmit={handleSubmit} className="space-y-5">
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

          <Field label="Título" required value={form.title} onChange={set('title')} />
          <Field
            label="Autores"
            required
            value={form.authors}
            onChange={set('authors')}
            hint="Separe por vírgula. Ex.: Eiichiro Oda, Masashi Kishimoto"
          />
          <div className="grid gap-5 sm:grid-cols-2">
            <Field
              label="ISBN"
              required
              minLength={10}
              value={form.isbn}
              onChange={set('isbn')}
              hint="Mínimo de 10 dígitos."
            />
            <Field label="Editora" required value={form.publisher} onChange={set('publisher')} />
          </div>
          <Field
            label="Gêneros"
            required
            value={form.genres}
            onChange={set('genres')}
            hint="Separe por vírgula. Ex.: Aventura, Fantasia"
          />
          <Field
            label="Temas (opcional)"
            value={form.themes}
            onChange={set('themes')}
            hint="Separe por vírgula."
          />

          {error && <Alert>{error}</Alert>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Salvando…' : 'Cadastrar'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
