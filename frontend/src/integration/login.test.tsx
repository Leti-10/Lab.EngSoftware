import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, authResponse } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('login', () => {
  it('entra sem persistir o JWT no navegador e mostra o nome na navbar', async () => {
    server.use(http.post(`${API}/auth/login`, () => HttpResponse.json(authResponse)))
    const { user } = renderApp('/login')

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha123')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('button', { name: 'ana' })).toBeInTheDocument()
    expect(localStorage.getItem('estante.token')).toBeNull()
    expect(await screen.findByRole('heading', { name: /Sua estante/ })).toBeInTheDocument()
  })

  it('envia e-mail e senha no corpo da requisição', async () => {
    let body: unknown
    server.use(
      http.post(`${API}/auth/login`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(authResponse)
      }),
    )
    const { user } = renderApp('/login')

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha123')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    await waitFor(() => expect(body).toEqual({ email: 'ana@example.com', password: 'senha123' }))
  })

  it('mostra o erro da API e não cria uma sessão com credenciais inválidas', async () => {
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
    expect(localStorage.getItem('estante.token')).toBeNull()
  })
})

describe('sessão', () => {
  it('restaura a sessão consultando o servidor e remove o token legado', async () => {
    signIn()
    renderApp('/')

    expect(await screen.findByRole('button', { name: 'ana' })).toBeInTheDocument()
    expect(localStorage.getItem('estante.token')).toBeNull()
  })

  it('mantém a sessão encerrada quando o servidor rejeita o cookie', async () => {
    localStorage.setItem('estante.token', 'expirado')
    server.use(
      http.get(`${API}/auth/me`, () =>
        HttpResponse.json({ detail: 'Sessão inválida' }, { status: 401 }),
      ),
    )
    renderApp('/')

    expect(await screen.findByRole('link', { name: 'Entrar' })).toBeInTheDocument()
    expect(localStorage.getItem('estante.token')).toBeNull()
  })

  it('encerra a sessão no servidor e leva ao login', async () => {
    signIn()
    const { user } = renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'ana' }))
    await user.click(screen.getByRole('button', { name: 'Sair' }))

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
    expect(localStorage.getItem('estante.token')).toBeNull()
  })

  it('mostra erro e preserva a sessão se o logout falhar', async () => {
    signIn()
    server.use(
      http.post(`${API}/auth/logout`, () =>
        HttpResponse.json({ detail: 'Falha ao encerrar a sessão.' }, { status: 500 }),
      ),
    )
    const { user } = renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'ana' }))
    await user.click(screen.getByRole('button', { name: 'Sair' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível encerrar a sessão: Falha ao encerrar a sessão.',
    )
    expect(screen.getByRole('button', { name: 'ana' })).toBeInTheDocument()
  })
})
