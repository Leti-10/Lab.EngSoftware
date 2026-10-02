import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('navbar', () => {
  it('mostra entrar e cadastrar para visitantes', () => {
    renderApp('/')

    expect(screen.getByRole('link', { name: 'Entrar' })).toHaveAttribute('href', '/login')
    expect(screen.getByRole('link', { name: 'Cadastrar' })).toHaveAttribute('href', '/cadastro')
    expect(screen.queryByRole('button', { name: 'ana' })).toBeNull()
  })

  it('mostra o botão de cadastrar obra e o menu para quem está logado', async () => {
    signIn()
    renderApp('/')

    expect(await screen.findByRole('button', { name: 'ana' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Cadastrar obra' })).toHaveAttribute(
      'href',
      '/livros/novo',
    )
    expect(screen.queryByRole('link', { name: 'Entrar' })).toBeNull()
  })
})

describe('menu do usuário', () => {
  async function openMenu() {
    signIn()
    const view = renderApp('/')
    const trigger = await screen.findByRole('button', { name: 'ana' })
    await view.user.click(trigger)
    return { ...view, trigger }
  }

  it('abre com nome, e-mail e as opções da conta', async () => {
    const { trigger } = await openMenu()

    expect(trigger).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByRole('menu')).toHaveTextContent('ana@example.com')
    expect(screen.getByRole('menuitem', { name: 'Meu perfil' })).toHaveAttribute('href', '/perfil')
    expect(screen.getByRole('menuitem', { name: 'Minhas listas' })).toHaveAttribute(
      'href',
      '/listas',
    )
    expect(screen.getByRole('menuitem', { name: 'Sair' })).toBeInTheDocument()
  })

  it('fecha com Esc', async () => {
    const { user } = await openMenu()

    await user.keyboard('{Escape}')

    expect(screen.queryByRole('menu')).toBeNull()
  })

  it('fecha ao clicar fora', async () => {
    const { user } = await openMenu()

    await user.click(screen.getByRole('heading', { name: /Sua estante/ }))

    expect(screen.queryByRole('menu')).toBeNull()
  })

  it('leva ao perfil e fecha o menu', async () => {
    server.use(http.get(`${API}/lists`, () => HttpResponse.json([])))
    const { user } = await openMenu()

    await user.click(screen.getByRole('menuitem', { name: 'Meu perfil' }))

    expect(await screen.findByRole('heading', { name: 'ana' })).toBeInTheDocument()
    expect(screen.queryByRole('menu')).toBeNull()
  })

  it('sair encerra a sessão e leva ao login', async () => {
    const { user } = await openMenu()

    await user.click(screen.getByRole('menuitem', { name: 'Sair' }))

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Entrar' })).toBeInTheDocument()
  })
})
