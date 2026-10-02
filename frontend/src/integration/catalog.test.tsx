import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, onePiece } from '../test/fixtures'
import { renderApp } from '../test/render'
import { server } from '../test/server'

describe('estante (catálogo)', () => {
  it('cada obra aponta para o seu detalhe', async () => {
    server.use(http.get(`${API}/books`, () => HttpResponse.json([onePiece])))
    renderApp('/livros')

    expect(await screen.findByRole('link', { name: /One Piece/ })).toHaveAttribute(
      'href',
      '/livros/1',
    )
  })

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
})
