import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { UserAvatar } from '../components/UserAvatar'
import { Alert, Button, Card, Field } from '../components/ui'
import { ApiError, api } from '../lib/api'
import type { User } from '../lib/types'

const MAX_BIO = 300

function urlError(value: string) {
  const text = value.trim()
  if (text && !/^https?:\/\//i.test(text))
    return 'Use um endereço que comece com http:// ou https://'
  return undefined
}

export function EditProfilePage() {
  const { user, updateUser } = useAuth()
  const navigate = useNavigate()
  const [bio, setBio] = useState(user?.bio ?? '')
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url ?? '')
  const [coverUrl, setCoverUrl] = useState(user?.cover_url ?? '')
  const [showErrors, setShowErrors] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  if (!user) return null

  const avatarError = showErrors ? urlError(avatarUrl) : undefined
  const coverError = showErrors ? urlError(coverUrl) : undefined

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setShowErrors(true)
    if (urlError(avatarUrl) || urlError(coverUrl)) return

    setSaving(true)
    try {
      const saved = await api<User>('/auth/me', {
        method: 'PUT',
        body: JSON.stringify({ bio, avatar_url: avatarUrl, cover_url: coverUrl }),
      })
      updateUser(saved)
      navigate('/perfil')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Não foi possível salvar o perfil.')
      setSaving(false)
    }
  }

  const coverPreview = coverUrl.trim() && !urlError(coverUrl) ? coverUrl.trim() : null

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-3xl font-semibold">Editar perfil</h1>
      <p className="mt-1 text-sm text-ink-soft">
        Personalize sua bio, seu avatar e sua capa. As imagens são links de endereços públicos.
      </p>

      <Card className="mt-8">
        <form onSubmit={handleSubmit} noValidate className="space-y-5">
          <div className="flex items-center gap-4">
            <UserAvatar
              username={user.username}
              url={avatarUrl.trim() && !urlError(avatarUrl) ? avatarUrl.trim() : null}
              className="size-20 shrink-0 rounded-full border-2 border-blue-warm-500 text-3xl"
            />
            <div className="min-w-0 flex-1">
              <Field
                label="Avatar (link da imagem)"
                type="url"
                inputMode="url"
                value={avatarUrl}
                onChange={(event) => setAvatarUrl(event.target.value)}
                placeholder="https://exemplo.com/minha-foto.jpg"
                error={avatarError}
              />
            </div>
          </div>

          <div>
            <Field
              label="Capa (link da imagem)"
              type="url"
              inputMode="url"
              value={coverUrl}
              onChange={(event) => setCoverUrl(event.target.value)}
              placeholder="https://exemplo.com/minha-capa.jpg"
              error={coverError}
            />
            <div
              aria-hidden="true"
              className="relative mt-3 h-28 overflow-hidden rounded-xl bg-blue-warm-100"
            >
              {coverPreview && (
                <img
                  src={coverPreview}
                  alt=""
                  className="absolute inset-0 size-full object-cover"
                />
              )}
            </div>
          </div>

          <div>
            <label htmlFor="profile-bio" className="mb-1.5 block text-sm font-medium text-ink">
              Bio
            </label>
            <textarea
              id="profile-bio"
              rows={4}
              maxLength={MAX_BIO}
              value={bio}
              onChange={(event) => setBio(event.target.value)}
              placeholder="Conte um pouco sobre você e o que gosta de ler"
              className="w-full rounded-xl border border-cream-300 bg-cream-50 px-4 py-2.5 text-sm text-ink placeholder:text-ink-soft/60 focus:border-blue-warm-500 focus:outline-none"
            />
            <p className="mt-1 text-right text-xs text-ink-soft">
              {bio.length}/{MAX_BIO}
            </p>
          </div>

          {error && <Alert>{error}</Alert>}

          <div className="flex gap-2">
            <Button type="submit" disabled={saving}>
              {saving ? 'Salvando…' : 'Salvar perfil'}
            </Button>
            <Link to="/perfil">
              <Button type="button" variant="ghost">
                Cancelar
              </Button>
            </Link>
          </div>
        </form>
      </Card>
    </div>
  )
}
