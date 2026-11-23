import { screen, waitFor, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import type { Review } from '../lib/types'
import { API, onePiece, review } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

function mockPage(reviews: Review[]) {
  server.use(
    http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
    http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
    http.get(`${API}/reviews`, () => HttpResponse.json(reviews)),
  )
}

describe('avaliações e resenhas', () => {
  it('mostra a média, a quantidade e as resenhas da obra', async () => {
    mockPage([
      review,
      { ...review, id: 11, rating: 5, username: 'caio', comment: 'Muito bom', likes: 0 },
    ])
    renderApp('/livros/1')

    expect(await screen.findByText('4,5')).toBeInTheDocument()
    expect(screen.getByText('2 avaliações')).toBeInTheDocument()
    expect(screen.getByText('bia')).toBeInTheDocument()
    expect(screen.getByText('Uma aventura incrível')).toBeInTheDocument()
  })

  it('convida visitantes a entrar para resenhar', async () => {
    mockPage([])
    renderApp('/livros/1')

    expect(await screen.findByText('Ainda não há resenhas para esta obra.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Entre' })).toHaveAttribute('href', '/login')
    expect(screen.queryByRole('radiogroup')).toBeNull()
  })

  it('borra a resenha com spoiler até clicar em mostrar', async () => {
    mockPage([{ ...review, isSpoiler: true, comment: 'O final é surpreendente' }])
    const { user } = renderApp('/livros/1')

    const button = await screen.findByRole('button', { name: 'Mostrar spoiler' })
    expect(screen.getByText('O final é surpreendente')).toHaveClass('blur-sm')

    await user.click(button)

    expect(screen.getByText('O final é surpreendente')).not.toHaveClass('blur-sm')
    expect(screen.queryByRole('button', { name: 'Mostrar spoiler' })).toBeNull()
  })

  it('publica a nota e a resenha com a marca de spoiler', async () => {
    signIn()
    mockPage([])
    let sent: unknown
    server.use(
      http.post(`${API}/reviews`, async ({ request }) => {
        sent = await request.json()
        return HttpResponse.json(
          { ...review, id: 20, user_id: 1, username: 'ana', rating: 5, likes: 0 },
          { status: 201 },
        )
      }),
    )
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('radio', { name: '5 estrelas' }))
    await user.type(screen.getByLabelText('Sua resenha'), 'Adorei')
    await user.click(screen.getByLabelText('Contém spoiler'))
    await user.click(screen.getByRole('button', { name: 'Publicar resenha' }))

    await waitFor(() =>
      expect(sent).toEqual({ rating: 5, comment: 'Adorei', isSpoiler: true, book_id: 1 }),
    )
    expect(await screen.findByRole('button', { name: 'Editar minha resenha' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Publicar resenha' })).toBeNull()
  })

  it('exige uma nota antes de publicar', async () => {
    signIn()
    mockPage([])
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('button', { name: 'Publicar resenha' }))

    expect(screen.getByRole('alert')).toHaveTextContent('Escolha de 1 a 5 estrelas.')
  })

  it('edita a própria resenha', async () => {
    signIn()
    mockPage([{ ...review, id: 30, user_id: 1, username: 'ana', rating: 3 }])
    let sent: unknown
    server.use(
      http.put(`${API}/reviews/30`, async ({ request }) => {
        sent = await request.json()
        return HttpResponse.json({
          ...review,
          id: 30,
          user_id: 1,
          username: 'ana',
          rating: 5,
          comment: 'Mudei de ideia',
        })
      }),
    )
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('button', { name: 'Editar minha resenha' }))
    const comment = screen.getByLabelText('Sua resenha')
    await user.clear(comment)
    await user.type(comment, 'Mudei de ideia')
    await user.click(screen.getByRole('radio', { name: '5 estrelas' }))
    await user.click(screen.getByRole('button', { name: 'Salvar alterações' }))

    await waitFor(() =>
      expect(sent).toEqual({ rating: 5, comment: 'Mudei de ideia', isSpoiler: false }),
    )
    expect(await screen.findByText('Mudei de ideia')).toBeInTheDocument()
  })

  it('curte e descurte uma resenha', async () => {
    signIn()
    mockPage([review])
    server.use(
      http.post(`${API}/votes`, () =>
        HttpResponse.json(
          { id: 7, status: 'like', target_entity: 'reviews', target_id: 10, user_id: 1 },
          { status: 201 },
        ),
      ),
      http.delete(`${API}/votes/7`, () => new HttpResponse(null, { status: 204 })),
    )
    const { user } = renderApp('/livros/1')

    const like = await screen.findByRole('button', { name: 'Curtir resenha' })
    expect(within(like).getByText('2')).toBeInTheDocument()

    await user.click(like)
    const liked = await screen.findByRole('button', { name: 'Descurtir resenha' })
    expect(within(liked).getByText('3')).toBeInTheDocument()

    await user.click(liked)
    expect(await screen.findByRole('button', { name: 'Curtir resenha' })).toHaveTextContent('2')
  })

  it('desabilita o curtir para visitantes', async () => {
    mockPage([review])
    renderApp('/livros/1')

    expect(await screen.findByRole('button', { name: 'Curtir resenha' })).toBeDisabled()
  })
})
