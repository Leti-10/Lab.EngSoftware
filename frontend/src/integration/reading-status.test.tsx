import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

function mockPage(current: 'reading' | null) {
  server.use(
    http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
    http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
    http.get(`${API}/reviews`, () => HttpResponse.json([])),
    http.get(`${API}/readings`, () =>
      HttpResponse.json(current ? [{ id: 1, book_id: 1, status: current }] : []),
    ),
  )
}

describe('status de leitura', () => {
  it('marca a obra como lendo e desmarca ao clicar de novo', async () => {
    signIn()
    mockPage(null)
    const bodies: unknown[] = []
    server.use(
      http.put(`${API}/readings/1`, async ({ request }) => {
        bodies.push(await request.json())
        return HttpResponse.json({ id: 1, book_id: 1, status: 'reading' })
      }),
      http.delete(`${API}/readings/1`, () => new HttpResponse(null, { status: 204 })),
    )
    const { user } = renderApp('/livros/1')

    const lendo = await screen.findByRole('button', { name: 'Lendo' })
    await user.click(lendo)
    await waitFor(() => expect(lendo).toHaveAttribute('aria-pressed', 'true'))
    expect(bodies).toEqual([{ status: 'reading' }])

    await user.click(lendo)
    await waitFor(() => expect(lendo).toHaveAttribute('aria-pressed', 'false'))
  })

  it('mostra o status já salvo', async () => {
    signIn()
    mockPage('reading')
    renderApp('/livros/1')

    expect(await screen.findByRole('button', { name: 'Lendo', pressed: true })).toBeInTheDocument()
  })

  it('desabilita as marcações para visitantes', async () => {
    mockPage(null)
    renderApp('/livros/1')

    expect(await screen.findByRole('button', { name: 'Lendo' })).toBeDisabled()
  })
})
