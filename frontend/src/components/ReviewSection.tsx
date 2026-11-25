import { Heart, MessageCircle } from 'lucide-react'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { ApiError, api } from '../lib/api'
import type { Review, ReviewPayload, Vote } from '../lib/types'
import { CommentSection } from './CommentSection'
import { RatingInput, Stars } from './StarRating'
import { Alert, Button, Card } from './ui'

const MAX_COMMENT = 1000

function ReviewForm({
  bookId,
  mine,
  onSaved,
  onCancel,
}: {
  bookId: number
  mine: Review | undefined
  onSaved: (review: Review) => void
  onCancel?: () => void
}) {
  const [rating, setRating] = useState(mine?.rating ?? 0)
  const [comment, setComment] = useState(mine?.comment ?? '')
  const [isSpoiler, setIsSpoiler] = useState(mine?.isSpoiler ?? false)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (rating === 0) {
      setError('Escolha de 1 a 5 estrelas.')
      return
    }
    setError(null)
    setSaving(true)
    const payload: ReviewPayload = {
      rating,
      comment: comment.trim() || null,
      isSpoiler,
    }
    try {
      const saved = mine
        ? await api<Review>(`/reviews/${mine.id}`, {
            method: 'PUT',
            body: JSON.stringify(payload),
          })
        : await api<Review>('/reviews', {
            method: 'POST',
            body: JSON.stringify({ ...payload, book_id: bookId }),
          })
      onSaved(saved)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível salvar a resenha.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-4">
      <div>
        <p className="mb-1.5 text-sm font-medium text-ink">Sua nota</p>
        <RatingInput value={rating} onChange={setRating} />
      </div>
      <div>
        <label htmlFor="review-comment" className="mb-1.5 block text-sm font-medium text-ink">
          Sua resenha
        </label>
        <textarea
          id="review-comment"
          rows={4}
          maxLength={MAX_COMMENT}
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          placeholder="O que você achou da obra? (opcional)"
          className="w-full rounded-xl border border-line bg-cream-50 px-4 py-2.5 text-sm text-ink placeholder:text-ink-soft focus:border-blue-warm-500 focus:outline-none"
        />
        <p className="mt-1 text-right text-xs text-ink-soft">
          {comment.length}/{MAX_COMMENT}
        </p>
      </div>
      <label className="flex items-center gap-2 text-sm text-ink">
        <input
          type="checkbox"
          checked={isSpoiler}
          onChange={(event) => setIsSpoiler(event.target.checked)}
          className="size-4 accent-blue-warm-600"
        />
        Contém spoiler
      </label>
      {error && <Alert>{error}</Alert>}
      <div className="flex gap-2">
        <Button type="submit" disabled={saving}>
          {saving ? 'Salvando…' : mine ? 'Salvar alterações' : 'Publicar resenha'}
        </Button>
        {onCancel && (
          <Button type="button" variant="ghost" onClick={onCancel} disabled={saving}>
            Cancelar
          </Button>
        )}
      </div>
    </form>
  )
}

export function ReviewItem({
  review,
  isMine = false,
  bookTitle,
  onEdit,
  onChange,
}: {
  review: Review
  isMine?: boolean
  bookTitle?: string | null
  onEdit?: () => void
  onChange: (review: Review) => void
}) {
  const { user } = useAuth()
  const [revealed, setRevealed] = useState(false)
  const [busy, setBusy] = useState(false)
  const [showComments, setShowComments] = useState(false)
  const hidden = review.isSpoiler && !revealed

  async function toggleLike() {
    setBusy(true)
    try {
      if (review.liked_by_me && review.like_vote_id !== null) {
        await api(`/votes/${review.like_vote_id}`, { method: 'DELETE' })
        onChange({
          ...review,
          liked_by_me: false,
          like_vote_id: null,
          likes: Math.max(0, review.likes - 1),
        })
      } else {
        const vote = await api<Vote>('/votes', {
          method: 'POST',
          body: JSON.stringify({
            status: 'like',
            target_entity: 'reviews',
            target_id: review.id,
          }),
        })
        onChange({ ...review, liked_by_me: true, like_vote_id: vote.id, likes: review.likes + 1 })
      }
    } catch {
      return
    } finally {
      setBusy(false)
    }
  }

  return (
    <li className="rounded-2xl border border-line bg-cream-50 p-5">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
        <Link to={`/usuarios/${review.user_id}`} className="font-medium text-ink hover:underline">
          {review.username ?? 'Leitor'}
        </Link>
        <Stars value={review.rating} size="size-4" />
        <span className="sr-only">{review.rating} de 5 estrelas</span>
        {review.isSpoiler && (
          <span className="rounded-full bg-cream-200 px-2.5 py-0.5 text-xs text-ink-soft">
            Spoiler
          </span>
        )}
        {isMine && onEdit && (
          <button
            type="button"
            onClick={onEdit}
            className="ml-auto text-xs font-medium text-blue-warm-600 hover:underline"
          >
            Editar minha resenha
          </button>
        )}
      </div>

      {bookTitle && (
        <p className="mt-2 text-sm text-ink-soft">
          sobre{' '}
          <Link
            to={`/livros/${review.book_id}`}
            className="font-medium text-blue-warm-600 hover:underline"
          >
            {bookTitle}
          </Link>
        </p>
      )}

      {review.comment && (
        <div className="mt-3">
          <p
            className={`text-sm leading-relaxed whitespace-pre-line text-ink transition ${
              hidden ? 'blur-sm select-none' : ''
            }`}
            aria-hidden={hidden || undefined}
          >
            {review.comment}
          </p>
          {hidden && (
            <button
              type="button"
              onClick={() => setRevealed(true)}
              className="mt-2 text-xs font-medium text-blue-warm-600 hover:underline"
            >
              Mostrar spoiler
            </button>
          )}
        </div>
      )}

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={toggleLike}
          disabled={!user || busy}
          aria-pressed={review.liked_by_me}
          aria-label={review.liked_by_me ? 'Descurtir resenha' : 'Curtir resenha'}
          title={user ? undefined : 'Entre para curtir'}
          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs transition-colors disabled:cursor-not-allowed ${
            review.liked_by_me
              ? 'bg-blue-warm-50 text-blue-warm-700'
              : 'text-ink-soft hover:bg-cream-200 disabled:hover:bg-transparent'
          }`}
        >
          <Heart
            aria-hidden="true"
            className="size-4"
            fill={review.liked_by_me ? 'currentColor' : 'none'}
          />
          <span aria-label={`${review.likes} curtidas`}>{review.likes}</span>
        </button>
        <button
          type="button"
          onClick={() => setShowComments((current) => !current)}
          aria-expanded={showComments}
          className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs text-ink-soft transition-colors hover:bg-cream-200"
        >
          <MessageCircle aria-hidden="true" className="size-4" />
          Comentários
        </button>
      </div>
      {showComments && <CommentSection reviewId={review.id} />}
    </li>
  )
}

export function ReviewSection({
  bookId,
  reviews,
  onChange,
}: {
  bookId: number
  reviews: Review[]
  onChange: (reviews: Review[]) => void
}) {
  const { user } = useAuth()
  const mine = user ? reviews.find((review) => review.user_id === user.id) : undefined
  const [editing, setEditing] = useState(false)

  function replace(updated: Review) {
    const exists = reviews.some((review) => review.id === updated.id)
    onChange(
      exists
        ? reviews.map((review) => (review.id === updated.id ? updated : review))
        : [updated, ...reviews],
    )
  }

  return (
    <section id="resenhas" aria-labelledby="resenhas-titulo" className="mt-12 scroll-mt-6">
      <h2 id="resenhas-titulo" className="text-xl font-semibold">
        Resenhas{reviews.length > 0 && ` (${reviews.length})`}
      </h2>

      <div className="mt-4">
        {!user && (
          <Card>
            <p className="text-sm text-ink-soft">
              <Link to="/login" className="font-medium text-blue-warm-600 hover:underline">
                Entre
              </Link>{' '}
              para avaliar e resenhar esta obra.
            </p>
          </Card>
        )}
        {user && (!mine || editing) && (
          <Card>
            <ReviewForm
              key={mine?.id ?? 'new'}
              bookId={bookId}
              mine={mine}
              onCancel={mine ? () => setEditing(false) : undefined}
              onSaved={(saved) => {
                replace(saved)
                setEditing(false)
              }}
            />
          </Card>
        )}
      </div>

      {reviews.length === 0 ? (
        <p className="mt-4 text-sm text-ink-soft">Ainda não há resenhas para esta obra.</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {reviews.map((review) => (
            <ReviewItem
              key={review.id}
              review={review}
              isMine={review.id === mine?.id}
              onEdit={() => setEditing(true)}
              onChange={replace}
            />
          ))}
        </ul>
      )}
    </section>
  )
}
