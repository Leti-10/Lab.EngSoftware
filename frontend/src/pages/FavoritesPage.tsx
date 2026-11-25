import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { BookCard } from '../components/BookCard'

export function FavoritesPage() {
  const { favorites, favoritesError, favoritesLoading } = useAuth()

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
          <div className="grid grid-cols-2 gap-x-5 gap-y-8 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {favorites.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
