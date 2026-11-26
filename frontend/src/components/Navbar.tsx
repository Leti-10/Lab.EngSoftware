import { BookOpen, House, Library, Newspaper, Plus } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { NotificationBell } from './NotificationBell'
import { UserMenu } from './UserMenu'

function NavItem({ to, icon, children }: { to: string; icon: ReactNode; children: ReactNode }) {
  return (
    <NavLink
      to={to}
      end={to === '/'}
      className={({ isActive }) =>
        `flex items-center gap-2 rounded-full px-3 py-1.5 text-sm transition-colors ${
          isActive
            ? 'bg-blue-warm-50 font-medium text-blue-warm-600'
            : 'text-ink-soft hover:bg-cream-200 hover:text-ink'
        }`
      }
    >
      {icon}
      <span className="hidden sm:inline">{children}</span>
    </NavLink>
  )
}

export function Navbar() {
  const { user } = useAuth()

  return (
    <header className="sticky top-0 z-10 border-b border-cream-300 bg-cream-50/85 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-2 px-4 py-3 sm:flex-nowrap sm:gap-4 sm:px-5">
        <div className="flex items-center gap-3 sm:gap-6">
          <Link
            to="/"
            className="flex items-center gap-2 font-serif text-xl font-semibold text-blue-warm-600"
          >
            <BookOpen aria-hidden="true" className="size-6" />
            Estante
          </Link>
          <nav aria-label="Principal" className="flex items-center gap-1">
            <NavItem to="/" icon={<House aria-hidden="true" className="size-4" />}>
              Início
            </NavItem>
            <NavItem to="/livros" icon={<Library aria-hidden="true" className="size-4" />}>
              Estante
            </NavItem>
            <NavItem to="/resenhas" icon={<Newspaper aria-hidden="true" className="size-4" />}>
              Resenhas
            </NavItem>
          </nav>
        </div>

        <div className="ml-auto flex shrink-0 items-center gap-2 sm:ml-0">
          {user ? (
            <>
              <Link
                to="/livros/novo"
                aria-label="Cadastrar obra"
                className="flex items-center gap-2 rounded-full bg-blue-warm-600 px-4 py-2 text-sm font-medium text-cream-50 transition-colors hover:bg-blue-warm-700"
              >
                <Plus aria-hidden="true" className="size-4" />
                <span className="hidden sm:inline">Cadastrar obra</span>
              </Link>
              <NotificationBell />
              <UserMenu />
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="rounded-full px-4 py-2 text-sm text-ink-soft transition-colors hover:bg-cream-200 hover:text-ink"
              >
                Entrar
              </Link>
              <Link
                to="/cadastro"
                className="rounded-full bg-blue-warm-600 px-4 py-2 text-sm font-medium text-cream-50 transition-colors hover:bg-blue-warm-700"
              >
                Cadastrar
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
