import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, onePiece } from '../test/fixtures'
import { renderApp } from '../test/render'
import { server } from '../test/server'

describe('detalhe da obra', () => {
  it('mostra dados, gêneros (sem repetir o tipo) e temas', async () => {
    server.use(http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)))
    renderApp('/livros/1')

    expect(await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })).toBeInTheDocument()
    expect(screen.getByText('por Eiichiro Oda')).toBeInTheDocument()
    expect(screen.getByText('Panini')).toBeInTheDocument()
    expect(screen.getByText('9788542603835')).toBeInTheDocument()
    expect(screen.getByText('Aventura')).toBeInTheDocument()
    expect(screen.getByText('Amizade')).toBeInTheDocument()
    expect(screen.getAllByText('Mangá')).toHaveLength(1)
  })

  it('oculta a seção de temas quando não há temas', async () => {
    server.use(http.get(`${API}/books/2`, () => HttpResponse.json(domCasmurro)))
    renderApp('/livros/2')

    await screen.findByRole('heading', { name: 'Dom Casmurro' })
    expect(screen.queryByText('Temas')).toBeNull()
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
