import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `text-sm transition-colors ${isActive ? 'font-medium text-blue-warm-600' : 'text-ink-soft hover:text-ink'}`

export function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="border-b border-cream-300 bg-cream-50/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-4">
        <Link to="/" className="font-serif text-xl font-semibold text-blue-warm-600">
          Estante
        </Link>
        <nav className="flex items-center gap-6">
          <NavLink to="/" end className={linkClass}>
            Início
          </NavLink>
          <NavLink to="/livros" className={linkClass}>
            Estante
          </NavLink>
          {user ? (
            <>
              <NavLink to="/listas" className={linkClass}>
                Minhas listas
              </NavLink>
              <NavLink to="/livros/novo" className={linkClass}>
                Cadastrar obra
              </NavLink>
              <span className="hidden text-sm text-ink-soft sm:inline">Olá, {user.username}</span>
              <button
                onClick={handleLogout}
                className="text-sm text-ink-soft transition-colors hover:text-ink"
              >
                Sair
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={linkClass}>
                Entrar
              </NavLink>
              <NavLink
                to="/cadastro"
                className="rounded-full bg-blue-warm-600 px-4 py-1.5 text-sm font-medium text-cream-50 transition-colors hover:bg-blue-warm-700"
              >
                Cadastrar
              </NavLink>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
