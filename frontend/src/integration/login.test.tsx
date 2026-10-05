import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { tokenStorage } from '../lib/api'
import { API, tokenResponse } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('login', () => {
  it('entra, salva o token e mostra o nome na navbar', async () => {
    server.use(http.post(`${API}/auth/login`, () => HttpResponse.json(tokenResponse)))
    const { user } = renderApp('/login')

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha123')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('button', { name: 'ana' })).toBeInTheDocument()
    expect(tokenStorage.get()).toBe('token-123')
    expect(await screen.findByRole('heading', { name: /Sua estante/ })).toBeInTheDocument()
  })

  it('envia e-mail e senha no corpo da requisição', async () => {
    let body: unknown
    server.use(
      http.post(`${API}/auth/login`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(tokenResponse)
      }),
    )
    const { user } = renderApp('/login')

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha123')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    await waitFor(() => expect(body).toEqual({ email: 'ana@example.com', password: 'senha123' }))
  })

  it('mostra o erro da API e não salva token com credenciais inválidas', async () => {
    server.use(
      http.post(`${API}/auth/login`, () =>
        HttpResponse.json({ detail: 'E-mail ou senha inválidos.' }, { status: 401 }),
      ),
    )
    const { user } = renderApp('/login')

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'errada')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('E-mail ou senha inválidos.')
    expect(tokenStorage.get()).toBeNull()
  })
})

describe('sessão', () => {
  it('restaura a sessão a partir do token salvo', async () => {
    signIn()
    renderApp('/')

    expect(await screen.findByRole('button', { name: 'ana' })).toBeInTheDocument()
  })

  it('descarta um token inválido', async () => {
    tokenStorage.set('expirado')
    server.use(
      http.get(`${API}/auth/me`, () =>
        HttpResponse.json({ detail: 'Sessão inválida' }, { status: 401 }),
      ),
    )
    renderApp('/')

    expect(await screen.findByRole('link', { name: 'Entrar' })).toBeInTheDocument()
    expect(tokenStorage.get()).toBeNull()
  })

  it('sair limpa o token e leva ao login', async () => {
    signIn()
    const { user } = renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'ana' }))
    await user.click(screen.getByRole('menuitem', { name: 'Sair' }))

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
    expect(tokenStorage.get()).toBeNull()
  })
})
