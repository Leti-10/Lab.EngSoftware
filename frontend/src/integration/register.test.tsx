import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { tokenStorage } from '../lib/api'
import { API, tokenResponse } from '../test/fixtures'
import { renderApp } from '../test/render'
import { server } from '../test/server'

describe('cadastro', () => {
  it('é acessível pelo link da tela de login', async () => {
    const { user } = renderApp('/login')

    await user.click(screen.getByRole('link', { name: 'Cadastre-se' }))

    expect(await screen.findByRole('heading', { name: 'Crie sua estante' })).toBeInTheDocument()
  })

  async function fillForm(user: ReturnType<typeof renderApp>['user'], confirm = 'senha123') {
    await user.type(screen.getByLabelText('Nome de usuário'), 'ana')
    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha123')
    await user.type(screen.getByLabelText('Confirmar senha'), confirm)
    await user.click(screen.getByRole('button', { name: 'Criar conta' }))
  }

  it('cria a conta e já entra logada', async () => {
    server.use(
      http.post(`${API}/auth/register`, () => HttpResponse.json(tokenResponse, { status: 201 })),
    )
    const { user } = renderApp('/cadastro')

    await fillForm(user)

    expect(await screen.findByRole('button', { name: 'ana' })).toBeInTheDocument()
    expect(tokenStorage.get()).toBe('token-123')
  })

  it('bloqueia quando as senhas não conferem, sem chamar a API', async () => {
    const { user } = renderApp('/cadastro')

    await fillForm(user, 'outra-senha')

    expect(await screen.findByText('As senhas não conferem.')).toBeInTheDocument()
  })

  it('mostra erro de e-mail já cadastrado (409)', async () => {
    server.use(
      http.post(`${API}/auth/register`, () =>
        HttpResponse.json({ detail: 'E-mail já cadastrado' }, { status: 409 }),
      ),
    )
    const { user } = renderApp('/cadastro')

    await fillForm(user)

    expect(await screen.findByRole('alert')).toHaveTextContent('E-mail já cadastrado')
  })
})
