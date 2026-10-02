import { useState } from 'react'
import type { FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Alert, Button, Card, Field } from '../components/ui'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: string } | null)?.from ?? '/'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to={from} replace />

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await login(email, password)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível entrar.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm py-8">
      <h1 className="text-center text-3xl font-semibold">Bem-vinda de volta</h1>
      <p className="mt-2 text-center text-sm text-ink-soft">
        Entre para ver sua estante e suas listas.
      </p>

      <Card className="mt-8">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field
            label="E-mail"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="voce@email.com"
          />
          <Field
            label="Senha"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <Alert>{error}</Alert>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Entrando…' : 'Entrar'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
