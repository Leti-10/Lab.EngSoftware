import { ChevronRight, Library, ListChecks, Mail, Plus, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { BookCover } from '../components/BookCard'
import { Card } from '../components/ui'
import { api } from '../lib/api'
import { kindOf } from '../lib/books'
import type { Book, BookList } from '../lib/types'

const ROLES: Record<string, string> = {
  user: 'Leitor(a)',
  developer: 'Desenvolvedor(a)',
  admin: 'Administrador(a)',
}

function StatCard({ label, value, unit }: { label: string; value: number | string; unit: string }) {
  return (
    <div className="rounded-2xl bg-cream-200/70 p-5">
      <p className="text-sm font-medium text-ink">{label}</p>
      <p className="mt-3 font-serif text-3xl font-semibold text-blue-warm-600">{value}</p>
      <p className="text-sm text-ink-soft">{unit}</p>
    </div>
  )
}

function ShortcutLink({
  to,
  icon,
  children,
}: {
  to: string
  icon: ReactNode
  children: ReactNode
}) {
  return (
    <Link
      to={to}
      className="flex items-center justify-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-cream-50 transition-colors hover:bg-cream-50/15"
    >
      {icon}
      {children}
    </Link>
  )
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

  const saved = new Map<number, Book>()
  lists?.forEach((list) => list.books.forEach((book) => saved.set(book.id, book)))
  const savedBooks = [...saved.values()]
  const count = (kind: string) => savedBooks.filter((book) => kindOf(book.genre) === kind).length
  const total = (value: number | undefined) => (lists === null ? '–' : (value ?? 0))

  const publicLists = lists?.filter((list) => !list.private).length
  const privateLists = lists?.filter((list) => list.private).length
  const role = ROLES[user.role] ?? user.role

  return (
    <div className="grid gap-8 md:grid-cols-[240px_1fr]">
      <aside className="space-y-5">
        <span
          aria-hidden="true"
          className="grid aspect-square w-full place-items-center rounded-2xl border-2 border-blue-warm-500 bg-blue-warm-100 font-serif text-7xl font-semibold text-blue-warm-700 uppercase"
        >
          {user.username.charAt(0)}
        </span>

        <Card className="space-y-4 p-5">
          <div className="flex items-center gap-3 text-sm">
            <Mail aria-hidden="true" className="size-4 shrink-0 text-ink-soft" />
            <span className="truncate">{user.email}</span>
          </div>
          <div className="flex items-center gap-3 text-sm">
            <ShieldCheck aria-hidden="true" className="size-4 shrink-0 text-ink-soft" />
            <span>{role}</span>
          </div>
        </Card>
      </aside>

      <div className="min-w-0">
        <h1 className="truncate text-3xl font-semibold">{user.username}</h1>

        <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard label="Listas" value={total(lists?.length)} unit="listas" />
          <StatCard label="Obras salvas" value={total(savedBooks.length)} unit="obras" />
          <StatCard label="Públicas" value={total(publicLists)} unit="listas" />
          <StatCard label="Privadas" value={total(privateLists)} unit="listas" />
        </div>

        <nav
          aria-label="Atalhos do perfil"
          className="mt-5 grid gap-1 rounded-2xl bg-blue-warm-600 p-2 sm:grid-cols-3"
        >
          <ShortcutLink to="/livros" icon={<Library aria-hidden="true" className="size-4" />}>
            Estante
          </ShortcutLink>
          <ShortcutLink to="/listas" icon={<ListChecks aria-hidden="true" className="size-4" />}>
            Minhas listas {lists?.length ?? 0}
          </ShortcutLink>
          <ShortcutLink to="/livros/novo" icon={<Plus aria-hidden="true" className="size-4" />}>
            Cadastrar obra
          </ShortcutLink>
        </nav>

        <div className="mt-10 grid gap-8 lg:grid-cols-[1fr_240px]">
          <section>
            <h2 className="text-xl font-semibold">Suas listas</h2>

            {lists?.length === 0 && (
              <p className="mt-4 text-sm text-ink-soft">
                Você ainda não criou nenhuma lista.{' '}
                <Link to="/listas" className="font-medium text-blue-warm-600 hover:underline">
                  Criar uma lista
                </Link>
              </p>
            )}

            <div className="mt-4 space-y-8">
              {lists?.slice(0, 3).map((list) => (
                <div key={list.id}>
                  <div className="flex items-center justify-between gap-4">
                    <h3 className="truncate font-sans text-sm font-semibold">{list.name}</h3>
                    <Link
                      to={`/listas/${list.id}`}
                      className="flex shrink-0 items-center gap-1 text-sm font-medium text-blue-warm-600 hover:underline"
                    >
                      Ver mais
                      <ChevronRight aria-hidden="true" className="size-4" />
                    </Link>
                  </div>
                  {list.books.length === 0 ? (
                    <p className="mt-3 text-sm text-ink-soft">Esta lista ainda está vazia.</p>
                  ) : (
                    <div className="mt-3 flex gap-3 overflow-x-auto pb-1">
                      {list.books.slice(0, 6).map((book) => (
                        <Link
                          key={book.id}
                          to={`/livros/${book.id}`}
                          aria-label={book.title}
                          className="w-24 shrink-0"
                        >
                          <BookCover book={book} />
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>

          <aside className="h-fit rounded-2xl bg-cream-200/70 p-5">
            <p className="font-serif text-lg font-semibold">{savedBooks.length} obras salvas</p>
            <ul className="mt-3 space-y-2 text-sm text-ink-soft">
              <li>Livros: {count('Livro')}</li>
              <li>Mangás: {count('Mangá')}</li>
              <li>Quadrinhos: {count('Quadrinhos')}</li>
            </ul>
          </aside>
        </div>
      </div>
    </div>
  )
}
