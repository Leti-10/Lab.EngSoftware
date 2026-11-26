import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { FollowButton } from '../components/FollowButton'
import { UserAvatar } from '../components/UserAvatar'
import { Alert } from '../components/ui'
import { ApiError, api } from '../lib/api'
import { useDocumentTitle } from '../lib/pageTitle'
import type { BookList, PublicProfile } from '../lib/types'

function Cover({ url }: { url: string | null }) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null)

  return (
    <div
      aria-hidden="true"
      className="relative mb-8 h-36 overflow-hidden rounded-2xl bg-blue-warm-100 sm:h-48"
    >
      {url && failedUrl !== url && (
        <img
          src={url}
          alt=""
          onError={() => setFailedUrl(url)}
          className="absolute inset-0 size-full object-cover"
        />
      )}
    </div>
  )
}

function UserProfile({ id }: { id: string | undefined }) {
  const { user } = useAuth()
  const [profile, setProfile] = useState<PublicProfile | null>(null)
  useDocumentTitle(profile?.username)
  const [lists, setLists] = useState<BookList[]>([])
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let cancelled = false
    api<PublicProfile>(`/users/${id}`)
      .then((data) => !cancelled && setProfile(data))
      .catch((err: ApiError) => !cancelled && setError(err))
    api<BookList[]>(`/users/${id}/lists`)
      .then((data) => !cancelled && setLists(data))
      .catch(() => undefined)
    return () => {
      cancelled = true
    }
  }, [id])

  if (error) {
    return <Alert>{error.status === 404 ? 'Usuário não encontrado.' : error.message}</Alert>
  }
  if (!profile) return <p className="text-ink-soft">Carregando…</p>

  const isMe = user?.id === profile.id

  return (
    <div>
      <Cover url={profile.cover_url} />
      <div className="flex flex-wrap items-center gap-5">
        <UserAvatar
          username={profile.username}
          url={profile.avatar_url}
          className="size-24 shrink-0 rounded-full border-2 border-blue-warm-500 text-4xl"
        />
        <div className="min-w-0 flex-1">
          <h1 className="truncate text-3xl font-semibold">{profile.username}</h1>
          <p className="mt-1 text-sm text-ink-soft">
            {profile.followers} {profile.followers === 1 ? 'seguidor' : 'seguidores'} ·{' '}
            {profile.following} seguindo
          </p>
        </div>
        {isMe ? (
          <Link to="/perfil" className="text-sm font-medium text-blue-warm-600 hover:underline">
            Ver meu perfil
          </Link>
        ) : (
          <FollowButton target="users" id={profile.id} />
        )}
      </div>

      {profile.bio && (
        <p className="mt-5 max-w-prose text-sm leading-relaxed whitespace-pre-line text-ink">
          {profile.bio}
        </p>
      )}

      <section aria-labelledby="listas-publicas" className="mt-10">
        <h2 id="listas-publicas" className="text-xl font-semibold">
          Listas públicas
        </h2>
        {lists.length === 0 ? (
          <p className="mt-3 text-sm text-ink-soft">Nenhuma lista pública ainda.</p>
        ) : (
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {lists.map((list) => (
              <li key={list.id}>
                <Link
                  to={`/listas/${list.id}`}
                  className="block rounded-2xl border border-cream-300 bg-cream-50 p-4 transition-colors hover:bg-cream-200"
                >
                  <p className="font-medium text-ink">{list.name}</p>
                  <p className="mt-1 line-clamp-2 text-sm text-ink-soft">{list.description}</p>
                  <p className="mt-2 text-xs text-blue-warm-600">
                    {list.books.length} {list.books.length === 1 ? 'obra' : 'obras'}
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

export function UserPage() {
  const { id } = useParams()

  return <UserProfile key={id} id={id} />
}
