import { Link, NavLink } from 'react-router-dom'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `text-sm transition-colors ${isActive ? 'font-medium text-blue-warm-600' : 'text-ink-soft hover:text-ink'}`

export function Navbar() {
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
        </nav>
      </div>
    </header>
  )
}
