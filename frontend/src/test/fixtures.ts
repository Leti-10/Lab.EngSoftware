import type { AuthResponse, Book, BookList, Review, User } from '../lib/types'

export const API = 'http://localhost:8000'

export const user: User = { id: 1, username: 'ana', email: 'ana@example.com', role: 'user' }

export const authResponse: AuthResponse = { user }

export const onePiece: Book = {
  id: 1,
  isbn: '9788542603835',
  title: 'One Piece, Vol. 1',
  publisher: 'Panini',
  authors: ['Eiichiro Oda'],
  genre: ['Mangá', 'Aventura'],
  theme: ['Amizade'],
}

export const domCasmurro: Book = {
  id: 2,
  isbn: '9788535902778',
  title: 'Dom Casmurro',
  publisher: 'Companhia das Letras',
  authors: ['Machado de Assis'],
  genre: ['Romance'],
  theme: [],
}

export const favoritos: BookList = {
  id: 1,
  owner: 1,
  name: 'Favoritos',
  description: 'Os que eu mais amo',
  private: false,
  books: [],
}

export const review: Review = {
  id: 10,
  rating: 4,
  comment: 'Uma aventura incrível',
  isSpoiler: false,
  user_id: 2,
  book_id: 1,
  username: 'bia',
  likes: 2,
  liked_by_me: false,
  like_vote_id: null,
  created_at: '2024-06-15T12:00:00Z',
}
