import { useEffect, useRef, useState } from 'react'
import { ChevronDown, ListChecks, LogOut, UserRound } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const itemClass =
  'flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm text-ink transition-colors hover:bg-cream-200'

export function UserMenu() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const container = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return

    function handleClick(event: MouseEvent) {
      if (!container.current?.contains(event.target as Node)) setOpen(false)
    }
    function handleKey(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false)
    }

    document.addEventListener('mousedown', handleClick)
    document.addEventListener('keydown', handleKey)
    return () => {
      document.removeEventListener('mousedown', handleClick)
      document.removeEventListener('keydown', handleKey)
    }
  }, [open])

  if (!user) return null

  function handleLogout() {
    setOpen(false)
    logout()
    navigate('/login')
  }

  return (
    <div ref={container} className="relative">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
        className="flex items-center gap-2 rounded-full border border-cream-300 bg-cream-50 py-1 pr-3 pl-1 text-sm text-ink transition-colors hover:bg-cream-200"
      >
        <span
          aria-hidden="true"
          className="grid size-7 place-items-center rounded-full bg-blue-warm-100 text-xs font-semibold text-blue-warm-700 uppercase"
        >
          {user.username.charAt(0)}
        </span>
        <span className="hidden max-w-28 truncate sm:inline">{user.username}</span>
        <ChevronDown
          aria-hidden="true"
          className={`size-4 text-ink-soft transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-2 w-60 rounded-2xl border border-cream-300 bg-cream-50 p-2 shadow-lg"
        >
          <div className="px-3 py-2">
            <p className="truncate text-sm font-semibold text-ink">{user.username}</p>
            <p className="truncate text-xs text-ink-soft">{user.email}</p>
          </div>
          <div className="my-1 border-t border-cream-300" />
          <Link to="/perfil" role="menuitem" onClick={() => setOpen(false)} className={itemClass}>
            <UserRound aria-hidden="true" className="size-4 text-ink-soft" />
            Meu perfil
          </Link>
          <Link to="/listas" role="menuitem" onClick={() => setOpen(false)} className={itemClass}>
            <ListChecks aria-hidden="true" className="size-4 text-ink-soft" />
            Minhas listas
          </Link>
          <div className="my-1 border-t border-cream-300" />
          <button type="button" role="menuitem" onClick={handleLogout} className={itemClass}>
            <LogOut aria-hidden="true" className="size-4 text-ink-soft" />
            Sair
          </button>
        </div>
      )}
    </div>
  )
}
