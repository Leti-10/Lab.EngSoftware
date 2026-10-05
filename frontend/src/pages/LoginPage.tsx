import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Alert, Button, Card, Field } from '../components/ui'
import { compact, hasErrors, validateEmail } from '../lib/validation'
import type { FieldErrors } from '../lib/validation'

type LoginField = 'email' | 'password'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: string } | null)?.from ?? '/'

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<FieldErrors<LoginField>>({})
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to={from} replace />

  const clear = (field: LoginField) => setErrors((current) => ({ ...current, [field]: undefined }))

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    const found = compact<LoginField>({
      email: validateEmail(email),
      password: password ? undefined : 'Informe sua senha.',
    })
    setErrors(found)
    if (hasErrors(found)) return

    setSubmitting(true)
    try {
      await login(email.trim(), password)
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
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <Field
            label="E-mail"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value)
              clear('email')
            }}
            placeholder="voce@email.com"
            error={errors.email}
          />
          <Field
            label="Senha"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              clear('password')
            }}
            placeholder="Sua senha"
            error={errors.password}
          />
          {error && <Alert>{error}</Alert>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Entrando…' : 'Entrar'}
          </Button>
        </form>
      </Card>

      <p className="mt-6 text-center text-sm text-ink-soft">
        Ainda não tem conta?{' '}
        <Link to="/cadastro" className="font-medium text-blue-warm-600 hover:underline">
          Cadastre-se
        </Link>
      </p>
    </div>
  )
}
