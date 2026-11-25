import { Trash2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'
import type { ReviewComment } from '../lib/types'
import { Alert, Button } from './ui'

const MAX_COMMENT = 500

export function CommentSection({ reviewId }: { reviewId: number }) {
  const { user } = useAuth()
  const [comments, setComments] = useState<ReviewComment[] | null>(null)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [sending, setSending] = useState(false)

  useEffect(() => {
    let cancelled = false
    api<ReviewComment[]>(`/reviews/${reviewId}/comments`)
      .then((data) => !cancelled && setComments(data))
      .catch((err: Error) => !cancelled && setError(err.message))
    return () => {
      cancelled = true
    }
  }, [reviewId])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!text.trim()) return
    setError(null)
    setSending(true)
    try {
      const created = await api<ReviewComment>(`/reviews/${reviewId}/comments`, {
        method: 'POST',
        body: JSON.stringify({ text }),
      })
      setComments((current) => [...(current ?? []), created])
      setText('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível comentar.')
    } finally {
      setSending(false)
    }
  }

  async function handleDelete(comment: ReviewComment) {
    setError(null)
    try {
      await api(`/comments/${comment.id}`, { method: 'DELETE' })
      setComments((current) => (current ?? []).filter((item) => item.id !== comment.id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível apagar.')
    }
  }

  return (
    <div className="mt-4 border-t border-cream-300 pt-4">
      {comments === null && !error && <p className="text-sm text-ink-soft">Carregando…</p>}
      {comments?.length === 0 && <p className="text-sm text-ink-soft">Ainda sem comentários.</p>}
      {comments && comments.length > 0 && (
        <ul className="space-y-3">
          {comments.map((comment) => (
            <li key={comment.id} className="text-sm">
              <div className="flex items-center gap-2">
                <Link
                  to={`/usuarios/${comment.user_id}`}
                  className="font-medium text-ink hover:underline"
                >
                  {comment.username ?? 'Leitor'}
                </Link>
                {user?.id === comment.user_id && (
                  <button
                    type="button"
                    onClick={() => handleDelete(comment)}
                    aria-label="Apagar comentário"
                    className="ml-auto rounded p-1 text-ink-soft hover:bg-cream-200 hover:text-danger"
                  >
                    <Trash2 aria-hidden="true" className="size-4" />
                  </button>
                )}
              </div>
              <p className="mt-0.5 whitespace-pre-line text-ink">{comment.text}</p>
            </li>
          ))}
        </ul>
      )}

      {user ? (
        <form onSubmit={handleSubmit} className="mt-4 space-y-2">
          <label htmlFor={`comment-${reviewId}`} className="sr-only">
            Escreva um comentário
          </label>
          <textarea
            id={`comment-${reviewId}`}
            rows={2}
            maxLength={MAX_COMMENT}
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Escreva um comentário"
            className="w-full rounded-xl border border-line bg-cream-50 px-3 py-2 text-sm text-ink focus:border-blue-warm-500 focus:outline-none"
          />
          <Button type="submit" disabled={sending || !text.trim()}>
            {sending ? 'Enviando…' : 'Comentar'}
          </Button>
        </form>
      ) : (
        <p className="mt-3 text-sm text-ink-soft">
          <Link to="/login" className="font-medium text-blue-warm-600 hover:underline">
            Entre
          </Link>{' '}
          para comentar.
        </p>
      )}
      {error && (
        <div className="mt-3">
          <Alert>{error}</Alert>
        </div>
      )}
    </div>
  )
}
