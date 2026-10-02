import type { Book, TokenResponse, User } from '../lib/types'

export const API = 'http://localhost:8000'

export const user: User = { id: 1, username: 'ana', email: 'ana@example.com', role: 'user' }

export const tokenResponse: TokenResponse = {
  access_token: 'token-123',
  token_type: 'bearer',
  user,
}

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
