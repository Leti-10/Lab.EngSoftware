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
