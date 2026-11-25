export interface User {
  id: number
  username: string
  email: string
  role: string
  bio?: string | null
  avatar_url?: string | null
  cover_url?: string | null
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

export interface Report {
  id: number | null
  user_id: number
  target_id: number
  target_entity: string
  description: string
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

export type ReadingKind = 'want_to_read' | 'reading' | 'read'

export interface Reading {
  id: number
  book_id: number
  status: ReadingKind
}

export interface ReviewComment {
  id: number
  review_id: number
  user_id: number
  username: string | null
  text: string
  created_at: string
}

export type FollowTarget = 'users' | 'lists'

export interface FollowStatus {
  following: boolean
  followers: number
}

export interface PublicProfile {
  id: number
  username: string
  bio: string | null
  avatar_url: string | null
  cover_url: string | null
  followers: number
  following: number
  is_following: boolean
}

export type NotificationKind = 'like' | 'comment' | 'follow'

export interface AppNotification {
  id: number
  type: NotificationKind
  actor_id: number
  actor_username: string | null
  review_id: number | null
  book_id: number | null
  read: boolean
  created_at: string
}

export interface NotificationList {
  items: AppNotification[]
  unread: number
}

export interface NotificationPreferences {
  likes: boolean
  comments: boolean
  follows: boolean
}

export interface FeedItem extends Review {
  book_title: string | null
}

export interface Recommendation {
  book: Book
  reason: string
}
