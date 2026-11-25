import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('favoritos', () => {
  it('abre favoritos pelo menu do perfil', async () => {
    signIn()
    server.use(http.get(`${API}/votes/favorites`, () => HttpResponse.json([onePiece])))
    const { user } = renderApp('/')

    await user.click(await screen.findByRole('button', { name: /ana/ }))
    await user.click(screen.getByRole('menuitem', { name: 'Favoritos' }))

    expect(await screen.findByRole('heading', { name: 'Favoritos' })).toBeInTheDocument()
    expect(screen.getByText('One Piece, Vol. 1', { selector: 'p' })).toBeInTheDocument()
  })

  it('exige dois cliques para desfavoritar e atualiza o botão', async () => {
    let removals = 0
    signIn()
    server.use(
      http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
      http.get(`${API}/votes/favorites`, () => HttpResponse.json([onePiece])),
      http.delete(`${API}/votes/favorites/1`, () => {
        removals += 1
        return new HttpResponse(null, { status: 204 })
      }),
    )
    const { user } = renderApp('/livros')

    await user.click(await screen.findByRole('button', { name: 'Desfavoritar' }))
    expect(screen.getByRole('button', { name: 'Confirmar?' })).toBeInTheDocument()
    expect(removals).toBe(0)

    await user.click(screen.getByRole('button', { name: 'Confirmar?' }))

    await waitFor(() => expect(removals).toBe(1))
    expect(await screen.findByRole('button', { name: 'Favoritar' })).toBeInTheDocument()
  })

  it('favorita uma obra com um clique', async () => {
    let additions = 0
    signIn()
    server.use(
      http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
      http.get(`${API}/votes/favorites`, () => HttpResponse.json([])),
      http.put(`${API}/votes/favorites/1`, () => {
        additions += 1
        return new HttpResponse(null, { status: 204 })
      }),
    )
    const { user } = renderApp('/livros')

    await user.click(await screen.findByRole('button', { name: 'Favoritar' }))

    const favoriteButton = await screen.findByRole('button', { name: 'Desfavoritar' })
    expect(favoriteButton.querySelector('svg')).toHaveClass('favorite-pulse')
    expect(additions).toBe(1)
  })
})
