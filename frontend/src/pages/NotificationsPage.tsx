import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Alert, Button, Card } from '../components/ui'
import { api } from '../lib/api'
import type {
  AppNotification,
  NotificationList,
  NotificationKind,
  NotificationPreferences,
} from '../lib/types'

const PREFERENCES: { key: keyof NotificationPreferences; label: string }[] = [
  { key: 'likes', label: 'Curtidas nas minhas resenhas' },
  { key: 'comments', label: 'Comentários nas minhas resenhas' },
  { key: 'follows', label: 'Novos seguidores' },
]

const MESSAGES: Record<NotificationKind, string> = {
  like: 'curtiu a sua resenha',
  comment: 'comentou na sua resenha',
  follow: 'começou a seguir você',
}

function targetOf(item: AppNotification) {
  if (item.type === 'follow') return `/usuarios/${item.actor_id}`
  return item.book_id ? `/livros/${item.book_id}` : `/usuarios/${item.actor_id}`
}

export function NotificationsPage() {
  const [data, setData] = useState<NotificationList | null>(null)
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    api<NotificationList>('/notifications')
      .then((result) => !cancelled && setData(result))
      .catch((err: Error) => !cancelled && setError(err.message))
    api<NotificationPreferences>('/notifications/preferences')
      .then((result) => !cancelled && setPreferences(result))
      .catch(() => undefined)
    return () => {
      cancelled = true
    }
  }, [])

  async function markAllRead() {
    setError(null)
    try {
      await api('/notifications/read', { method: 'POST' })
      setData((current) =>
        current
          ? { unread: 0, items: current.items.map((item) => ({ ...item, read: true })) }
          : current,
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível atualizar.')
    }
  }

  async function open(item: AppNotification) {
    if (item.read) return
    try {
      await api(`/notifications/${item.id}/read`, { method: 'PATCH' })
      setData((current) =>
        current
          ? {
              unread: Math.max(0, current.unread - 1),
              items: current.items.map((other) =>
                other.id === item.id ? { ...other, read: true } : other,
              ),
            }
          : current,
      )
    } catch {
      return
    }
  }

  async function togglePreference(key: keyof NotificationPreferences) {
    if (!preferences) return
    const next = { ...preferences, [key]: !preferences[key] }
    setPreferences(next)
    setError(null)
    try {
      await api('/notifications/preferences', { method: 'PUT', body: JSON.stringify(next) })
    } catch (err) {
      setPreferences(preferences)
      setError(err instanceof Error ? err.message : 'Não foi possível salvar.')
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <h1 className="text-3xl font-semibold">Notificações</h1>
        <Button variant="ghost" onClick={markAllRead} disabled={!data || data.unread === 0}>
          Marcar todas como lidas
        </Button>
      </div>

      {error && (
        <div className="mt-4">
          <Alert>{error}</Alert>
        </div>
      )}

      <section aria-label="Lista de notificações" className="mt-6">
        {data === null && !error && <p className="text-ink-soft">Carregando…</p>}
        {data?.items.length === 0 && (
          <p className="py-10 text-center text-ink-soft">Você não tem notificações.</p>
        )}
        {data && data.items.length > 0 && (
          <ul className="space-y-2">
            {data.items.map((item) => (
              <li key={item.id}>
                <Link
                  to={targetOf(item)}
                  onClick={() => open(item)}
                  className={`block rounded-2xl border p-4 text-sm transition-colors hover:bg-cream-200 ${
                    item.read
                      ? 'border-cream-300 bg-cream-50 text-ink-soft'
                      : 'border-blue-warm-500 bg-blue-warm-50 text-ink'
                  }`}
                >
                  <strong className="font-semibold">{item.actor_username ?? 'Alguém'}</strong>{' '}
                  {MESSAGES[item.type]}
                  {!item.read && <span className="sr-only"> (não lida)</span>}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      {preferences && (
        <Card className="mt-10">
          <fieldset>
            <legend className="text-lg font-semibold">Preferências de notificação</legend>
            <p className="mt-1 text-sm text-ink-soft">Escolha o que você quer receber.</p>
            <div className="mt-4 space-y-3">
              {PREFERENCES.map(({ key, label }) => (
                <label key={key} className="flex items-center gap-3 text-sm text-ink">
                  <input
                    type="checkbox"
                    checked={preferences[key]}
                    onChange={() => togglePreference(key)}
                    className="size-4 accent-blue-warm-600"
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>
        </Card>
      )}
    </div>
  )
}
