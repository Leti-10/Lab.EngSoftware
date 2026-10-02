export interface User {
  id: number
  username: string
  email: string
  role: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Book {
  id: number
  isbn: string
  title: string
  publisher: string
  authors: string[]
  genre: string[]
  theme: string[]
}

export interface BookPayload {
  isbn: string
  title: string
  publisher: string
  authors: string[]
  genre: string[]
  theme: string[]
}

export interface BookList {
  id: number
  owner: number
  name: string
  description: string
  private: boolean
  books: Book[]
}

export interface Review {
  id: number
  rating: number
  comment: string | null
  isSpoiler: boolean
  user_id: number
  book_id: number
  username: string | null
  likes: number
  liked_by_me: boolean
  like_vote_id: number | null
}

export interface ReviewPayload {
  rating: number
  comment: string | null
  isSpoiler: boolean
}

export interface Vote {
  id: number
  status: string
  target_entity: string
  target_id: number
  user_id: number
}

export interface CatalogBook {
  isbn: string
  title: string
  authors: string[]
  publisher: string
  genres: string[]
  cover_url: string | null
}
