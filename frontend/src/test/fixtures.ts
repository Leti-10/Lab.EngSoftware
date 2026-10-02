import type { TokenResponse, User } from '../lib/types'

export const API = 'http://localhost:8000'

export const user: User = { id: 1, username: 'ana', email: 'ana@example.com', role: 'user' }

export const tokenResponse: TokenResponse = {
  access_token: 'token-123',
  token_type: 'bearer',
  user,
}
