import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, favoritos, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('perfil', () => {
  it('exige login', async () => {
    renderApp('/perfil')

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
  })

  it('mostra os dados da conta e o resumo das listas', async () => {
    server.use(
      http.get(`${API}/lists`, () =>
        HttpResponse.json([
          { ...favoritos, books: [onePiece, domCasmurro] },
          { ...favoritos, id: 2, name: 'Outra', books: [onePiece] },
        ]),
      ),
    )
    signIn()
    renderApp('/perfil')

    expect(await screen.findByRole('heading', { name: 'ana' })).toBeInTheDocument()
    expect(screen.getByText('ana@example.com')).toBeInTheDocument()
    expect(screen.getAllByText('Leitor(a)').length).toBeGreaterThan(0)
    expect(await screen.findByText('2')).toBeInTheDocument()
    expect(screen.getByText(/listas · 3 obras/)).toBeInTheDocument()
  })

  it('continua funcionando se as listas não carregarem', async () => {
    server.use(http.get(`${API}/lists`, () => HttpResponse.json({ detail: 'x' }, { status: 500 })))
    signIn()
    renderApp('/perfil')

    expect(await screen.findByText(/listas · 0 obras/)).toBeInTheDocument()
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
