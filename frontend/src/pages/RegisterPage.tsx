import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Alert, Button, Card, Field } from '../components/ui'
import { compact, hasErrors, validateEmail } from '../lib/validation'
import type { FieldErrors } from '../lib/validation'

type RegisterField = 'username' | 'email' | 'password' | 'confirm'

export function RegisterPage() {
  const { user, register } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [errors, setErrors] = useState<FieldErrors<RegisterField>>({})
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/" replace />

  const clear = (field: RegisterField) =>
    setErrors((current) => ({ ...current, [field]: undefined }))

  function validate() {
    let usernameError: string | undefined
    if (!username.trim()) usernameError = 'Escolha um nome de usuário.'
    else if (username.trim().length < 3)
      usernameError = 'O nome de usuário deve ter pelo menos 3 caracteres.'

    let passwordError: string | undefined
    if (!password) passwordError = 'Crie uma senha.'
    else if (password.length < 6) passwordError = 'A senha deve ter pelo menos 6 caracteres.'

    let confirmError: string | undefined
    if (!confirm) confirmError = 'Confirme sua senha.'
    else if (confirm !== password) confirmError = 'As senhas não conferem.'

    return compact<RegisterField>({
      username: usernameError,
      email: validateEmail(email),
      password: passwordError,
      confirm: confirmError,
    })
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    const found = validate()
    setErrors(found)
    if (hasErrors(found)) return

    setSubmitting(true)
    try {
      await register(username.trim(), email.trim(), password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível criar a conta.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-sm py-8">
      <h1 className="text-center text-3xl font-semibold">Crie sua estante</h1>
      <p className="mt-2 text-center text-sm text-ink-soft">
        Leva menos de um minuto e é de graça.
      </p>

      <Card className="mt-8">
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <Field
            label="Nome de usuário"
            autoComplete="username"
            value={username}
            onChange={(e) => {
              setUsername(e.target.value)
              clear('username')
            }}
            placeholder="Ex.: leticia"
            hint="Mínimo de 3 caracteres."
            error={errors.username}
          />
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
            autoComplete="new-password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              clear('password')
            }}
            placeholder="Crie uma senha"
            hint="Mínimo de 6 caracteres."
            error={errors.password}
          />
          <Field
            label="Confirmar senha"
            type="password"
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => {
              setConfirm(e.target.value)
              clear('confirm')
            }}
            placeholder="Repita a senha"
            error={errors.confirm}
          />
          {error && <Alert>{error}</Alert>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Criando conta…' : 'Criar conta'}
          </Button>
        </form>
      </Card>

      <p className="mt-6 text-center text-sm text-ink-soft">
        Já tem conta?{' '}
        <Link to="/login" className="font-medium text-blue-warm-600 hover:underline">
          Entrar
        </Link>
      </p>
    </div>
  )
}
