import { screen, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, favoritos, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

const sandman = { ...onePiece, id: 3, title: 'Sandman', genre: ['Quadrinhos'] }

describe('perfil', () => {
  it('exige login', async () => {
    renderApp('/perfil')

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
  })

  it('mostra nome, e-mail e tipo de conta', async () => {
    server.use(http.get(`${API}/lists`, () => HttpResponse.json([])))
    signIn()
    renderApp('/perfil')

    expect(await screen.findByRole('heading', { name: 'ana' })).toBeInTheDocument()
    expect(screen.getByText('ana@example.com')).toBeInTheDocument()
    expect(screen.getByText('Leitor(a)')).toBeInTheDocument()
  })

  it('resume listas e obras salvas, sem contar a mesma obra duas vezes', async () => {
    server.use(
      http.get(`${API}/lists`, () =>
        HttpResponse.json([
          { ...favoritos, books: [onePiece, domCasmurro] },
          { ...favoritos, id: 2, name: 'Secreta', private: true, books: [onePiece, sandman] },
        ]),
      ),
    )
    signIn()
    renderApp('/perfil')

    const resumo = await screen.findByText('3 obras salvas')
    const side = resumo.closest('aside') as HTMLElement
    expect(within(side).getByText('Livros: 1')).toBeInTheDocument()
    expect(within(side).getByText('Mangás: 1')).toBeInTheDocument()
    expect(within(side).getByText('Quadrinhos: 1')).toBeInTheDocument()
    expect(screen.getByText('Públicas').nextElementSibling).toHaveTextContent('1')
    expect(screen.getByText('Privadas').nextElementSibling).toHaveTextContent('1')
  })

  it('mostra as capas de cada lista e leva ao detalhe da obra', async () => {
    server.use(
      http.get(`${API}/lists`, () => HttpResponse.json([{ ...favoritos, books: [onePiece] }])),
    )
    signIn()
    renderApp('/perfil')

    expect(await screen.findByRole('heading', { name: 'Favoritos' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'One Piece, Vol. 1' })).toHaveAttribute(
      'href',
      '/livros/1',
    )
    expect(screen.getByRole('link', { name: 'Ver mais' })).toHaveAttribute('href', '/listas/1')
  })

  it('mostra aviso quando ainda não há listas', async () => {
    server.use(http.get(`${API}/lists`, () => HttpResponse.json([])))
    signIn()
    renderApp('/perfil')

    expect(await screen.findByText(/ainda não criou nenhuma lista/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Criar uma lista' })).toHaveAttribute('href', '/listas')
  })

  it('tem atalhos para estante, listas e cadastro de obra', async () => {
    server.use(http.get(`${API}/lists`, () => HttpResponse.json([favoritos])))
    signIn()
    renderApp('/perfil')

    const atalhos = await screen.findByRole('navigation', { name: 'Atalhos do perfil' })
    expect(within(atalhos).getByRole('link', { name: 'Estante' })).toHaveAttribute(
      'href',
      '/livros',
    )
    expect(within(atalhos).getByRole('link', { name: /Minhas listas/ })).toHaveAttribute(
      'href',
      '/listas',
    )
    expect(within(atalhos).getByRole('link', { name: 'Cadastrar obra' })).toHaveAttribute(
      'href',
      '/livros/novo',
    )
  })

  it('continua funcionando se as listas não carregarem', async () => {
    server.use(http.get(`${API}/lists`, () => HttpResponse.json({ detail: 'x' }, { status: 500 })))
    signIn()
    renderApp('/perfil')

    expect(await screen.findByText('0 obras salvas')).toBeInTheDocument()
  })
})

describe('página não encontrada', () => {
  it('aparece para endereços inexistentes', async () => {
    renderApp('/isso-nao-existe')

    expect(
      await screen.findByRole('heading', { name: 'Página não encontrada' }),
    ).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Voltar para o início' })).toHaveAttribute('href', '/')
  })

  it('o botão leva de volta ao início', async () => {
    const { user } = renderApp('/isso-nao-existe')

    await user.click(await screen.findByRole('link', { name: 'Voltar para o início' }))

    expect(await screen.findByRole('heading', { name: /Sua estante/ })).toBeInTheDocument()
  })
})
