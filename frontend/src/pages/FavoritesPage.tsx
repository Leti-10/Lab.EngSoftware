import { Search, SearchX } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { BookCard } from '../components/BookCard'

export function FavoritesPage() {
  const { favorites, favoritesError, favoritesLoading } = useAuth()
  const [titleFilter, setTitleFilter] = useState('')
  const filteredFavorites = useMemo(() => {
    const query = titleFilter.trim().toLocaleLowerCase()
    if (!query) return favorites
    return favorites.filter((book) => book.title.toLocaleLowerCase().includes(query))
  }, [favorites, titleFilter])

  return (
    <section>
      <div className="flex items-center gap-3">
        <h1 className="text-3xl font-semibold">Favoritos</h1>
      </div>
      <p className="mt-1 text-sm text-ink-soft">As obras que você favoritou.</p>

      <div className="mt-8">
        {!favoritesError && favoritesLoading && (
          <p className="text-ink-soft">Carregando favoritos…</p>
        )}
        {!favoritesError && !favoritesLoading && favorites.length === 0 && (
          <p className="py-12 text-center text-ink-soft">
            Você ainda não favoritou nenhuma obra.{' '}
            <Link to="/livros" className="font-medium text-blue-warm-600 hover:underline">
              Explorar a estante
            </Link>
          </p>
        )}
        {favorites.length > 0 && (
          <>
            <div className="relative mb-6 max-w-md">
              <Search
                aria-hidden="true"
                className="pointer-events-none absolute top-1/2 left-4 size-4 -translate-y-1/2 text-ink-soft"
              />
              <input
                type="search"
                value={titleFilter}
                onChange={(event) => setTitleFilter(event.target.value)}
                placeholder="Filtrar por título"
                aria-label="Filtrar favoritos por título"
                className="w-full rounded-full border border-line bg-cream-50 py-2.5 pr-5 pl-11 text-sm placeholder:text-ink-soft focus:border-blue-warm-500 focus:outline-none"
              />
            </div>
            {filteredFavorites.length === 0 ? (
              <p className="py-12 text-center text-ink-soft">
                <SearchX aria-hidden="true" className="mx-auto mb-3 size-8 text-blue-warm-500" />
                Nenhum favorito corresponde a esse título.
              </p>
            ) : (
              <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {filteredFavorites.map((book) => (
                  <BookCard key={book.id} book={book} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </section>
  )
}
