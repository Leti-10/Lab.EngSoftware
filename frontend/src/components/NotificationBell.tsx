import { Bell } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { api } from '../lib/api'
import type { NotificationList } from '../lib/types'

const REFRESH_MS = 60_000

export function NotificationBell() {
  const { user } = useAuth()
  const location = useLocation()
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    if (!user) return
    let cancelled = false
    const load = () =>
      api<NotificationList>('/notifications')
        .then((data) => !cancelled && setUnread(data.unread))
        .catch(() => undefined)
    load()
    const timer = setInterval(load, REFRESH_MS)
    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [user, location.pathname])

  if (!user) return null

  const label = unread > 0 ? `Notificações, ${unread} não lidas` : 'Notificações'

  return (
    <Link
      to="/notificacoes"
      aria-label={label}
      className="relative grid size-10 place-items-center rounded-full text-ink-soft transition-colors hover:bg-cream-200 hover:text-ink"
    >
      <Bell aria-hidden="true" className="size-5" />
      {unread > 0 && (
        <span
          aria-hidden="true"
          className="absolute top-1 right-1 grid min-w-4 place-items-center rounded-full bg-danger px-1 text-[10px] leading-4 font-semibold text-cream-50"
        >
          {unread > 9 ? '9+' : unread}
        </span>
      )}
    </Link>
  )
}
