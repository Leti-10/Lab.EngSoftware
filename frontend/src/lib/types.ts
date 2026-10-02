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
