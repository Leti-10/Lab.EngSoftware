import { UserCheck, UserPlus } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'
import type { FollowStatus, FollowTarget } from '../lib/types'
import { Alert } from './ui'

export function FollowButton({ target, id }: { target: FollowTarget; id: number }) {
  const { user } = useAuth()
  const [status, setStatus] = useState<FollowStatus | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api<FollowStatus>(`/follows/${target}/${id}`)
      .then((data) => !cancelled && setStatus(data))
      .catch(() => undefined)
    return () => {
      cancelled = true
    }
  }, [target, id, user])

  async function toggle() {
    if (!status) return
    setError(null)
    setBusy(true)
    try {
      setStatus(
        await api<FollowStatus>(`/follows/${target}/${id}`, {
          method: status.following ? 'DELETE' : 'PUT',
        }),
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível atualizar.')
    } finally {
      setBusy(false)
    }
  }

  const Icon = status?.following ? UserCheck : UserPlus

  return (
    <div>
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={toggle}
          disabled={!user || busy || !status}
          aria-pressed={status?.following ?? false}
          title={user ? undefined : 'Entre para seguir'}
          className={`inline-flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
            status?.following
              ? 'border-blue-warm-600 bg-blue-warm-600 text-cream-50'
              : 'border-blue-warm-100 text-blue-warm-600 hover:bg-blue-warm-50'
          }`}
        >
          <Icon aria-hidden="true" className="size-4" />
          {status?.following ? 'Seguindo' : 'Seguir'}
        </button>
        {status && (
          <span className="text-sm text-ink-soft">
            {status.followers} {status.followers === 1 ? 'seguidor' : 'seguidores'}
          </span>
        )}
      </div>
      {error && (
        <div className="mt-2">
          <Alert>{error}</Alert>
        </div>
      )}
    </div>
  )
}
