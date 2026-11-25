import { screen } from '@testing-library/react'
import axe from 'axe-core'
import { http, HttpResponse } from 'msw'
import { API, favoritos, onePiece, review } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

async function violationsIn(container: HTMLElement) {
  const result = await axe.run(container, {
    rules: { 'color-contrast': { enabled: false } },
  })
  return result.violations.map(
    (violation) =>
      `${violation.id}: ${violation.help} (${violation.nodes.map((node) => node.target.join(' ')).join(' | ')})`,
  )
}

const publicProfile = {
  id: 2,
  username: 'bia',
  bio: 'Leitora de mangás',
  avatar_url: null,
  cover_url: null,
  followers: 3,
  following: 1,
  is_following: false,
}

function mockApi() {
  server.use(
    http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
    http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
    http.get(`${API}/reviews`, () => HttpResponse.json([review])),
    http.get(`${API}/readings`, () => HttpResponse.json([])),
    http.get(`${API}/lists`, () => HttpResponse.json([favoritos])),
    http.get(`${API}/feed`, () => HttpResponse.json([{ ...review, book_title: 'One Piece' }])),
    http.get(`${API}/recommendations`, () =>
      HttpResponse.json([{ book: onePiece, reason: 'Porque você gosta de Oda' }]),
    ),
    http.get(`${API}/notifications/preferences`, () =>
      HttpResponse.json({ likes: true, comments: true, follows: true }),
    ),
    http.get(`${API}/users/2`, () => HttpResponse.json(publicProfile)),
    http.get(`${API}/users/2/lists`, () => HttpResponse.json([])),
    http.get(`${API}/follows/users/2`, () => HttpResponse.json({ following: false, followers: 3 })),
  )
}

const PAGES: { name: string; route: string; ready: string | RegExp; signedIn: boolean }[] = [
  { name: 'início', route: '/', ready: /Sua estante/, signedIn: false },
  { name: 'login', route: '/login', ready: 'Bem-vinda de volta', signedIn: false },
  { name: 'cadastro', route: '/cadastro', ready: 'Crie sua estante', signedIn: false },
  { name: 'estante', route: '/livros', ready: 'Estante', signedIn: true },
  { name: 'detalhe da obra', route: '/livros/1', ready: 'One Piece, Vol. 1', signedIn: true },
  { name: 'cadastrar obra', route: '/livros/novo', ready: 'Cadastrar obra', signedIn: true },
  { name: 'perfil', route: '/perfil', ready: 'ana', signedIn: true },
  { name: 'editar perfil', route: '/perfil/editar', ready: 'Editar perfil', signedIn: true },
  { name: 'minhas listas', route: '/listas', ready: /Minhas listas/, signedIn: true },
  { name: 'notificações', route: '/notificacoes', ready: 'Notificações', signedIn: true },
  { name: 'feed', route: '/feed', ready: 'Feed', signedIn: true },
  { name: 'recomendações', route: '/recomendacoes', ready: 'Recomendações', signedIn: true },
  { name: 'perfil público', route: '/usuarios/2', ready: 'bia', signedIn: true },
]

describe('acessibilidade (axe)', () => {
  it.each(PAGES)('a página $name não tem violações detectáveis', async (page) => {
    mockApi()
    if (page.signedIn) signIn()
    const { container } = renderApp(page.route)

    await screen.findByRole('heading', { name: page.ready, level: 1 })
    await screen.findAllByRole('main')

    expect(await violationsIn(container)).toEqual([])
  })
})

describe('navegação por teclado e leitores de tela', () => {
  it('oferece o link para pular ao conteúdo principal', async () => {
    mockApi()
    renderApp('/livros')

    const skip = await screen.findByRole('link', { name: 'Pular para o conteúdo' })

    expect(skip).toHaveAttribute('href', '#conteudo')
    expect(document.getElementById('conteudo')?.tagName).toBe('MAIN')
  })

  it('atualiza o título da aba e leva o foco ao conteúdo ao trocar de página', async () => {
    mockApi()
    signIn()
    const { user } = renderApp('/livros')
    await screen.findByRole('heading', { name: 'Estante', level: 1 })
    expect(document.title).toBe('Estante')

    await user.click(await screen.findByRole('button', { name: /ana/ }))
    await user.click(screen.getByRole('link', { name: 'Feed' }))

    await screen.findByRole('heading', { name: 'Feed', level: 1 })
    expect(document.title).toBe('Feed · Estante')
    expect(document.activeElement).toBe(document.getElementById('conteudo'))
  })

  it('usa o nome da obra como título da página de detalhe', async () => {
    mockApi()
    renderApp('/livros/1')

    await screen.findByRole('heading', { name: 'One Piece, Vol. 1', level: 1 })

    expect(document.title).toBe('One Piece, Vol. 1 · Estante')
  })

  it('fecha o menu da conta com Escape e devolve o foco ao botão', async () => {
    mockApi()
    signIn()
    const { user } = renderApp('/livros')
    const trigger = await screen.findByRole('button', { name: /ana/ })

    await user.click(trigger)
    expect(screen.getByRole('navigation', { name: 'Menu da conta' })).toBeInTheDocument()
    await user.keyboard('{Escape}')

    expect(screen.queryByRole('navigation', { name: 'Menu da conta' })).toBeNull()
    expect(document.activeElement).toBe(trigger)
  })
})
