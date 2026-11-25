import { screen, waitFor, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, onePiece } from '../test/fixtures'
import { renderApp } from '../test/render'
import { server } from '../test/server'

const naruto = {
  ...onePiece,
  id: 3,
  isbn: '9781569319000',
  title: 'Naruto, Vol. 1',
  authors: ['Masashi Kishimoto'],
  genre: ['Mangá', 'Aventura'],
}
const otherByOda = { ...onePiece, id: 4, isbn: '9781569319123', title: 'One Piece, Vol. 2' }

function mockBook(book = onePiece, extra: { author?: unknown[]; genre?: unknown[] } = {}) {
  server.use(
    http.get(`${API}/reviews`, () => HttpResponse.json([])),
    http.get(`${API}/readings`, () => HttpResponse.json([])),
    http.get(`${API}/books/${book.id}`, () => HttpResponse.json(book)),
    http.get(`${API}/books`, ({ request }) => {
      const params = new URL(request.url).searchParams
      if (params.get('q')) return HttpResponse.json(extra.author ?? [book])
      if (params.get('genre')) return HttpResponse.json(extra.genre ?? [book])
      return HttpResponse.json([book])
    }),
  )
}

describe('detalhe da obra', () => {
  it('mostra título, autores, editora e ISBN', async () => {
    mockBook()
    renderApp('/livros/1')

    expect(await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Eiichiro Oda' })).toHaveAttribute(
      'href',
      '/livros?q=Eiichiro%20Oda',
    )
    expect(screen.getByText('ISBN-13: 9788542603835')).toBeInTheDocument()
    expect(screen.getAllByText('Panini').length).toBeGreaterThan(0)
  })

  it('mostra o tipo da obra', async () => {
    mockBook(domCasmurro)
    renderApp('/livros/2')

    await screen.findByRole('heading', { name: 'Dom Casmurro' })
    expect(screen.getAllByText('Livro').length).toBeGreaterThan(0)
  })

  it('troca entre as abas de detalhes, gêneros e temas', async () => {
    mockBook()
    const { user } = renderApp('/livros/1')
    await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })

    expect(screen.getByRole('tab', { name: 'Detalhes' })).toHaveAttribute('aria-selected', 'true')

    await user.click(screen.getByRole('tab', { name: 'Gêneros' }))
    const panel = screen.getByRole('tabpanel')
    expect(within(panel).getByRole('link', { name: 'Aventura' })).toHaveAttribute(
      'href',
      '/livros?genre=Aventura',
    )
    expect(within(panel).queryByText('Mangá')).toBeNull()

    await user.click(screen.getByRole('tab', { name: 'Temas' }))
    expect(within(screen.getByRole('tabpanel')).getByText('Amizade')).toBeInTheDocument()
  })

  it('avisa quando não há temas', async () => {
    mockBook(domCasmurro)
    const { user } = renderApp('/livros/2')
    await screen.findByRole('heading', { name: 'Dom Casmurro' })

    await user.click(screen.getByRole('tab', { name: 'Temas' }))

    expect(screen.getByText('Nenhum tema informado.')).toBeInTheDocument()
  })

  it('lista outras obras do mesmo autor e obras parecidas, sem repetir a atual', async () => {
    mockBook(onePiece, { author: [onePiece, otherByOda], genre: [onePiece, naruto] })
    renderApp('/livros/1')

    const sameAuthor = await screen.findByRole('heading', { name: /Mais de Eiichiro Oda/ })
    const authorSection = sameAuthor.closest('section') as HTMLElement
    expect(
      within(authorSection).getByText('One Piece, Vol. 2', { selector: 'p' }),
    ).toBeInTheDocument()
    expect(within(authorSection).queryByText('One Piece, Vol. 1', { selector: 'p' })).toBeNull()

    const similar = await screen.findByRole('heading', { name: /Obras parecidas/ })
    const similarSection = similar.closest('section') as HTMLElement
    expect(
      within(similarSection).getByText('Naruto, Vol. 1', { selector: 'p' }),
    ).toBeInTheDocument()
  })

  it('esconde as seções de outras obras quando não há resultados', async () => {
    mockBook(onePiece, { author: [onePiece], genre: [onePiece] })
    renderApp('/livros/1')

    await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })
    await waitFor(() => expect(screen.queryByRole('heading', { name: /Mais de/ })).toBeNull())
    expect(screen.queryByRole('heading', { name: /Obras parecidas/ })).toBeNull()
  })

  it('mostra o atalho para resenhar e a avaliação vazia', async () => {
    mockBook()
    renderApp('/livros/1')

    await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })
    expect(screen.getByRole('link', { name: 'Resenhar' })).toHaveAttribute('href', '#resenhas')
    expect(screen.getByText('Ainda sem avaliações')).toBeInTheDocument()
  })

  it('mostra "Obra não encontrada" para 404', async () => {
    server.use(
      http.get(`${API}/books/99`, () =>
        HttpResponse.json({ detail: 'Livro 99 não encontrado.' }, { status: 404 }),
      ),
    )
    renderApp('/livros/99')

    expect(await screen.findByRole('alert')).toHaveTextContent('Obra não encontrada.')
    expect(screen.getByRole('link', { name: /Voltar para a estante/ })).toBeInTheDocument()
  })
})

describe('estante aberta pelo detalhe', () => {
  it('o link do autor abre a estante já buscando por ele', async () => {
    mockBook()
    server.use(
      http.get(`${API}/books`, ({ request }) => {
        const q = new URL(request.url).searchParams.get('q')
        return HttpResponse.json(q === 'Eiichiro Oda' ? [onePiece, otherByOda] : [onePiece])
      }),
    )
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('link', { name: 'Eiichiro Oda' }))

    expect(await screen.findByLabelText('Buscar por título ou autor')).toHaveValue('Eiichiro Oda')
    expect(await screen.findByText('One Piece, Vol. 2', { selector: 'p' })).toBeInTheDocument()
  })

  it('o link do gênero abre a estante filtrada e permite remover o filtro', async () => {
    const genres: (string | null)[] = []
    mockBook()
    server.use(
      http.get(`${API}/books`, ({ request }) => {
        genres.push(new URL(request.url).searchParams.get('genre'))
        return HttpResponse.json([onePiece])
      }),
    )
    const { user } = renderApp('/livros/1')
    await user.click(await screen.findByRole('tab', { name: 'Gêneros' }))

    await user.click(screen.getByRole('link', { name: 'Aventura' }))

    const remove = await screen.findByRole('button', { name: 'Remover filtro Aventura' })
    expect(genres).toContain('Aventura')

    await user.click(remove)

    expect(screen.queryByRole('button', { name: 'Remover filtro Aventura' })).toBeNull()
  })
})
