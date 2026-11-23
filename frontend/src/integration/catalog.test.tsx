import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('estante (catálogo)', () => {
  it('lista as obras cadastradas', async () => {
    server.use(http.get(`${API}/books`, () => HttpResponse.json([onePiece, domCasmurro])))
    renderApp('/livros')

    expect(await screen.findByText('One Piece, Vol. 1', { selector: 'p' })).toBeInTheDocument()
    expect(screen.getByText('Dom Casmurro', { selector: 'p' })).toBeInTheDocument()
  })

  it('mostra estado vazio com atalho para cadastrar', async () => {
    server.use(http.get(`${API}/books`, () => HttpResponse.json([])))
    renderApp('/livros')

    expect(await screen.findByText(/Nenhuma obra encontrada/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Cadastrar uma obra' })).toHaveAttribute(
      'href',
      '/livros/novo',
    )
  })

  it('busca no backend enviando o parâmetro q', async () => {
    const queries: (string | null)[] = []
    server.use(
      http.get(`${API}/books`, ({ request }) => {
        const q = new URL(request.url).searchParams.get('q')
        queries.push(q)
        return HttpResponse.json(q ? [domCasmurro] : [onePiece, domCasmurro])
      }),
    )
    const { user } = renderApp('/livros')
    await screen.findByText('One Piece, Vol. 1', { selector: 'p' })

    await user.type(screen.getByLabelText('Buscar por título ou autor'), 'casmurro')

    await waitFor(() =>
      expect(screen.queryByText('One Piece, Vol. 1', { selector: 'p' })).toBeNull(),
    )
    expect(screen.getByText('Dom Casmurro', { selector: 'p' })).toBeInTheDocument()
    expect(queries.filter(Boolean)).toEqual(['casmurro'])
  })

  it('filtra por Mangás enviando genre=Mangá', async () => {
    const genres: (string | null)[] = []
    server.use(
      http.get(`${API}/books`, ({ request }) => {
        const genre = new URL(request.url).searchParams.get('genre')
        genres.push(genre)
        return HttpResponse.json(genre ? [onePiece] : [onePiece, domCasmurro])
      }),
    )
    const { user } = renderApp('/livros')
    await screen.findByText('Dom Casmurro', { selector: 'p' })

    await user.click(screen.getByRole('button', { name: 'Mangás' }))

    await waitFor(() => expect(screen.queryByText('Dom Casmurro', { selector: 'p' })).toBeNull())
    expect(genres).toContain('Mangá')
    expect(screen.getByRole('button', { name: 'Mangás' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('mostra o erro quando a API falha', async () => {
    server.use(
      http.get(`${API}/books`, () => HttpResponse.json({ detail: 'Falhou' }, { status: 500 })),
    )
    renderApp('/livros')

    expect(await screen.findByRole('alert')).toHaveTextContent('Falhou')
  })

  it('abre o detalhe ao clicar em uma obra', async () => {
    server.use(
      http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
      http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
    )
    const { user } = renderApp('/livros')

    await user.click(await screen.findByRole('link', { name: /One Piece/ }))

    expect(await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })).toBeInTheDocument()
  })
})

describe('busca com obras do Open Library', () => {
  const fromOutside = {
    isbn: '9788535914849',
    title: 'Torto Arado',
    authors: ['Itamar Vieira Junior'],
    publisher: 'Todavia',
    genres: ['Romance'],
    cover_url: null,
  }

  it('mostra a obra de fora junto das locais e cadastra ao abrir', async () => {
    signIn()
    let sent: unknown
    server.use(
      http.get(`${API}/books`, ({ request }) =>
        HttpResponse.json(new URL(request.url).searchParams.get('q') ? [] : [domCasmurro]),
      ),
      http.get(`${API}/catalog/search`, () => HttpResponse.json([fromOutside])),
      http.post(`${API}/books`, async ({ request }) => {
        sent = await request.json()
        return HttpResponse.json(
          { ...domCasmurro, id: 50, ...fromOutside, theme: [], genre: ['Romance'] },
          { status: 201 },
        )
      }),
      http.get(`${API}/books/50`, () =>
        HttpResponse.json({ ...domCasmurro, id: 50, title: 'Torto Arado', genre: ['Romance'] }),
      ),
      http.get(`${API}/reviews`, () => HttpResponse.json([])),
    )
    const { user } = renderApp('/livros')
    await screen.findByText('Dom Casmurro', { selector: 'p' })

    await user.type(screen.getByLabelText('Buscar por título ou autor'), 'torto')
    await user.click(await screen.findByRole('button', { name: /Torto Arado/ }, { timeout: 3000 }))

    expect(await screen.findByRole('heading', { name: 'Torto Arado' })).toBeInTheDocument()
    expect(sent).toMatchObject({ isbn: '9788535914849', title: 'Torto Arado', genre: ['Romance'] })
  })

  it('não consulta o Open Library para visitantes', async () => {
    let called = false
    server.use(
      http.get(`${API}/books`, () => HttpResponse.json([])),
      http.get(`${API}/catalog/search`, () => {
        called = true
        return HttpResponse.json([fromOutside])
      }),
    )
    const { user } = renderApp('/livros')
    await user.type(await screen.findByLabelText('Buscar por título ou autor'), 'torto')

    expect(await screen.findByText(/Nenhuma obra encontrada/)).toBeInTheDocument()
    expect(called).toBe(false)
  })
})
