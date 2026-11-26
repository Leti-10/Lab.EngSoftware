import { screen, waitFor, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, favoritos, onePiece, review } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

const bia = {
  id: 2,
  username: 'bia',
  bio: 'Leitora de mangás',
  avatar_url: null,
  cover_url: null,
  followers: 3,
  following: 1,
  is_following: false,
}

function mockBook() {
  server.use(
    http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
    http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
    http.get(`${API}/reviews`, () => HttpResponse.json([review])),
    http.get(`${API}/readings`, () => HttpResponse.json([])),
  )
}

describe('comentários em resenhas', () => {
  it('abre os comentários, lê os existentes e publica um novo', async () => {
    signIn()
    mockBook()
    let sent: unknown
    server.use(
      http.get(`${API}/reviews/10/comments`, () =>
        HttpResponse.json([
          {
            id: 1,
            review_id: 10,
            user_id: 3,
            username: 'caio',
            text: 'Concordo',
            created_at: '2026-11-27T10:00:00Z',
          },
        ]),
      ),
      http.post(`${API}/reviews/10/comments`, async ({ request }) => {
        sent = await request.json()
        return HttpResponse.json(
          {
            id: 2,
            review_id: 10,
            user_id: 1,
            username: 'ana',
            text: 'Também amei',
            created_at: '2026-11-27T11:00:00Z',
          },
          { status: 201 },
        )
      }),
      http.delete(`${API}/comments/2`, () => new HttpResponse(null, { status: 204 })),
    )
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('button', { name: 'Comentários' }))
    expect(await screen.findByText('Concordo')).toBeInTheDocument()

    await user.type(screen.getByLabelText('Escreva um comentário'), 'Também amei')
    await user.click(screen.getByRole('button', { name: 'Comentar' }))

    expect(await screen.findByText('Também amei')).toBeInTheDocument()
    expect(sent).toEqual({ text: 'Também amei' })

    await user.click(screen.getByRole('button', { name: 'Apagar comentário' }))
    await waitFor(() => expect(screen.queryByText('Também amei')).toBeNull())
  })

  it('convida visitantes a entrar para comentar', async () => {
    mockBook()
    server.use(http.get(`${API}/reviews/10/comments`, () => HttpResponse.json([])))
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('button', { name: 'Comentários' }))

    expect(await screen.findByText('Ainda sem comentários.')).toBeInTheDocument()
    expect(screen.queryByLabelText('Escreva um comentário')).toBeNull()
  })
})

describe('perfil público e seguidores', () => {
  it('mostra o perfil, as listas públicas e segue a pessoa', async () => {
    signIn()
    server.use(
      http.get(`${API}/users/2`, () => HttpResponse.json(bia)),
      http.get(`${API}/users/2/lists`, () =>
        HttpResponse.json([{ ...favoritos, id: 5, owner: 2, books: [onePiece] }]),
      ),
      http.get(`${API}/follows/users/2`, () =>
        HttpResponse.json({ following: false, followers: 3 }),
      ),
      http.put(`${API}/follows/users/2`, () =>
        HttpResponse.json({ following: true, followers: 4 }),
      ),
      http.delete(`${API}/follows/users/2`, () =>
        HttpResponse.json({ following: false, followers: 3 }),
      ),
    )
    const { user } = renderApp('/usuarios/2')

    expect(await screen.findByRole('heading', { name: 'bia' })).toBeInTheDocument()
    expect(screen.getByText('Leitora de mangás')).toBeInTheDocument()
    expect(screen.getByText('3 seguidores · 1 seguindo')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Favoritos/ })).toHaveAttribute('href', '/listas/5')

    const follow = await screen.findByRole('button', { name: 'Seguir' })
    await user.click(follow)
    expect(await screen.findByRole('button', { name: 'Seguindo' })).toBeInTheDocument()
    expect(screen.getByText('4 seguidores')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Seguindo' }))
    expect(await screen.findByText('3 seguidores')).toBeInTheDocument()
  })

  it('mostra erro quando o usuário não existe', async () => {
    server.use(
      http.get(`${API}/users/99`, () =>
        HttpResponse.json({ detail: 'Usuário não encontrado.' }, { status: 404 }),
      ),
      http.get(`${API}/users/99/lists`, () => HttpResponse.json([])),
    )
    renderApp('/usuarios/99')

    expect(await screen.findByText('Usuário não encontrado.')).toBeInTheDocument()
  })

  it('em lista de outra pessoa mostra seguir e esconde o adicionar', async () => {
    signIn()
    server.use(
      http.get(`${API}/lists/5`, () =>
        HttpResponse.json({ ...favoritos, id: 5, owner: 2, books: [onePiece] }),
      ),
      http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
      http.get(`${API}/follows/lists/5`, () =>
        HttpResponse.json({ following: false, followers: 0 }),
      ),
    )
    renderApp('/listas/5')

    expect(await screen.findByRole('button', { name: 'Seguir' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Adicionar' })).toBeNull()
  })
})

describe('notificações', () => {
  const items = [
    {
      id: 1,
      type: 'like',
      actor_id: 2,
      actor_username: 'bia',
      review_id: 10,
      book_id: 1,
      read: false,
      created_at: '2026-11-27T10:00:00Z',
    },
    {
      id: 2,
      type: 'follow',
      actor_id: 3,
      actor_username: 'caio',
      review_id: null,
      book_id: null,
      read: true,
      created_at: '2026-11-27T09:00:00Z',
    },
  ]

  it('mostra o contador no sino do cabeçalho', async () => {
    signIn()
    server.use(
      http.get(`${API}/notifications`, () => HttpResponse.json({ items, unread: 1 })),
      http.get(`${API}/books`, () => HttpResponse.json([])),
    )
    renderApp('/livros')

    expect(await screen.findByRole('link', { name: 'Notificações, 1 não lidas' })).toHaveAttribute(
      'href',
      '/notificacoes',
    )
  })

  it('lista, marca todas como lidas e salva as preferências', async () => {
    signIn()
    let saved: { likes: boolean; comments: boolean; follows: boolean } | undefined
    server.use(
      http.get(`${API}/notifications`, () => HttpResponse.json({ items, unread: 1 })),
      http.get(`${API}/notifications/preferences`, () =>
        HttpResponse.json({ likes: true, comments: true, follows: true }),
      ),
      http.post(`${API}/notifications/read`, () => new HttpResponse(null, { status: 204 })),
      http.put(`${API}/notifications/preferences`, async ({ request }) => {
        const body = (await request.json()) as NonNullable<typeof saved>
        saved = body
        return HttpResponse.json(body)
      }),
    )
    const { user } = renderApp('/notificacoes')

    const list = await screen.findByRole('region', { name: 'Lista de notificações' })
    expect(await within(list).findByText(/curtiu a sua resenha/)).toBeInTheDocument()
    expect(within(list).getByText(/começou a seguir você/)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Marcar todas como lidas' }))
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Marcar todas como lidas' })).toBeDisabled(),
    )

    await user.click(await screen.findByRole('checkbox', { name: 'Novos seguidores' }))
    await waitFor(() => expect(saved).toEqual({ likes: true, comments: true, follows: false }))
  })

  it('mostra o estado vazio', async () => {
    signIn()
    renderApp('/notificacoes')

    expect(await screen.findByText('Você não tem notificações.')).toBeInTheDocument()
  })
})

describe('feed e recomendações', () => {
  it('mostra as resenhas de quem você segue com o título da obra', async () => {
    signIn()
    server.use(
      http.get(`${API}/feed`, () =>
        HttpResponse.json([{ ...review, book_title: 'One Piece, Vol. 1' }]),
      ),
    )
    renderApp('/feed')

    expect(await screen.findByText('Uma aventura incrível')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'One Piece, Vol. 1' })).toHaveAttribute(
      'href',
      '/livros/1',
    )
  })

  it('mostra o feed vazio com atalho para a estante', async () => {
    signIn()
    server.use(http.get(`${API}/feed`, () => HttpResponse.json([])))
    renderApp('/feed')

    expect(await screen.findByText(/Seu feed está vazio/)).toBeInTheDocument()
  })

  it('mostra as recomendações com o motivo', async () => {
    signIn()
    server.use(
      http.get(`${API}/recommendations`, () =>
        HttpResponse.json([{ book: onePiece, reason: 'Porque você gosta de Eiichiro Oda' }]),
      ),
    )
    renderApp('/recomendacoes')

    expect(await screen.findByText('Porque você gosta de Eiichiro Oda')).toBeInTheDocument()
    expect(screen.getByText('One Piece, Vol. 1', { selector: 'p' })).toBeInTheDocument()
  })

  it('explica como gerar recomendações quando não há nenhuma', async () => {
    signIn()
    server.use(http.get(`${API}/recommendations`, () => HttpResponse.json([])))
    renderApp('/recomendacoes')

    expect(await screen.findByText(/Ainda não temos o que recomendar/)).toBeInTheDocument()
  })

  it('exige login para o feed', async () => {
    renderApp('/feed')

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
  })
})
