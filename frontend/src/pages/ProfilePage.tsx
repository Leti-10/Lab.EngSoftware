import { ListChecks, Mail, Plus, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Card } from '../components/ui'
import { api } from '../lib/api'
import type { BookList } from '../lib/types'

const ROLES: Record<string, string> = {
  user: 'Leitor(a)',
  developer: 'Desenvolvedor(a)',
  admin: 'Administrador(a)',
}

export function ProfilePage() {
  const { user } = useAuth()
  const [lists, setLists] = useState<BookList[] | null>(null)

  useEffect(() => {
    api<BookList[]>('/lists')
      .then(setLists)
      .catch(() => setLists([]))
  }, [])

  if (!user) return null

  const books = lists?.reduce((total, list) => total + list.books.length, 0) ?? 0

  return (
    <div className="mx-auto max-w-2xl">
      <div className="flex items-center gap-5">
        <span
          aria-hidden="true"
          className="grid size-20 place-items-center rounded-full bg-blue-warm-100 font-serif text-3xl font-semibold text-blue-warm-700 uppercase"
        >
          {user.username.charAt(0)}
        </span>
        <div className="min-w-0">
          <h1 className="truncate text-3xl font-semibold">{user.username}</h1>
          <p className="mt-1 text-sm text-ink-soft">{ROLES[user.role] ?? user.role}</p>
        </div>
      </div>

      <Card className="mt-8">
        <h2 className="text-lg font-semibold">Conta</h2>
        <dl className="mt-4 space-y-4 text-sm">
          <div className="flex items-center gap-3">
            <Mail aria-hidden="true" className="size-4 text-ink-soft" />
            <dt className="w-24 text-ink-soft">E-mail</dt>
            <dd className="truncate">{user.email}</dd>
          </div>
          <div className="flex items-center gap-3">
            <ShieldCheck aria-hidden="true" className="size-4 text-ink-soft" />
            <dt className="w-24 text-ink-soft">Perfil</dt>
            <dd>{ROLES[user.role] ?? user.role}</dd>
          </div>
        </dl>
      </Card>

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <Link to="/listas" className="block">
          <Card className="h-full transition-colors hover:bg-blue-warm-50/40">
            <ListChecks aria-hidden="true" className="size-5 text-blue-warm-600" />
            <p className="mt-3 text-2xl font-semibold">{lists?.length ?? '–'}</p>
            <p className="text-sm text-ink-soft">
              {lists?.length === 1 ? 'lista' : 'listas'} · {books} {books === 1 ? 'obra' : 'obras'}
            </p>
          </Card>
        </Link>
        <Link to="/livros/novo" className="block">
          <Card className="h-full transition-colors hover:bg-blue-warm-50/40">
            <Plus aria-hidden="true" className="size-5 text-blue-warm-600" />
            <p className="mt-3 text-lg font-semibold">Cadastrar obra</p>
            <p className="text-sm text-ink-soft">Adicione um livro, mangá ou quadrinho.</p>
          </Card>
        </Link>
      </div>
    </div>
  )
}
