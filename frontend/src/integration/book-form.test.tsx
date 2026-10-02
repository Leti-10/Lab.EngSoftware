import { screen, waitFor, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('cadastrar obra', () => {
  async function fill(user: ReturnType<typeof renderApp>['user']) {
    await user.type(screen.getByLabelText('Título'), 'One Piece, Vol. 1')
    await user.type(screen.getByLabelText('Autores'), 'Eiichiro Oda, Outro Autor')
    await user.type(screen.getByLabelText('ISBN'), '9788542603835')
    await user.type(screen.getByLabelText('Editora'), 'Panini')
    await user.type(screen.getByLabelText('Gêneros'), 'Aventura, Shounen')
    await user.type(screen.getByLabelText('Temas (opcional)'), 'Amizade')
  }

  it('exige login', async () => {
    renderApp('/livros/novo')

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
  })

  it('envia o payload correto (tipo Mangá entra nos gêneros) e abre o detalhe', async () => {
    let body: unknown
    server.use(
      http.post(`${API}/books`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(onePiece, { status: 201 })
      }),
      http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
    )
    signIn()
    const { user } = renderApp('/livros/novo')
    await screen.findByRole('heading', { name: 'Cadastrar obra' })

    await user.click(screen.getByRole('button', { name: 'Mangá' }))
    await fill(user)
    await user.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })).toBeInTheDocument()
    expect(body).toEqual({
      isbn: '9788542603835',
      title: 'One Piece, Vol. 1',
      publisher: 'Panini',
      authors: ['Eiichiro Oda', 'Outro Autor'],
      genre: ['Mangá', 'Aventura', 'Shounen'],
      theme: ['Amizade'],
    })
  })

  it('tipo Livro não adiciona gênero extra', async () => {
    let body: { genre: string[] } | undefined
    server.use(
      http.post(`${API}/books`, async ({ request }) => {
        body = (await request.json()) as { genre: string[] }
        return HttpResponse.json(domCasmurro, { status: 201 })
      }),
      http.get(`${API}/books/2`, () => HttpResponse.json(domCasmurro)),
    )
    signIn()
    const { user } = renderApp('/livros/novo')
    await screen.findByRole('heading', { name: 'Cadastrar obra' })

    await fill(user)
    await user.click(screen.getByRole('button', { name: 'Cadastrar' }))

    await waitFor(() => expect(body?.genre).toEqual(['Aventura', 'Shounen']))
  })

  it('mostra erro de ISBN duplicado e mantém o formulário preenchido', async () => {
    server.use(
      http.post(`${API}/books`, () =>
        HttpResponse.json({ detail: 'ISBN já cadastrado' }, { status: 409 }),
      ),
    )
    signIn()
    const { user } = renderApp('/livros/novo')
    await screen.findByRole('heading', { name: 'Cadastrar obra' })

    await fill(user)
    await user.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('ISBN já cadastrado')
    expect(screen.getByLabelText('Título')).toHaveValue('One Piece, Vol. 1')
  })

  it('alterna o tipo selecionado', async () => {
    signIn()
    const { user } = renderApp('/livros/novo')
    await screen.findByRole('heading', { name: 'Cadastrar obra' })
    const group = screen.getByRole('group', { name: 'Tipo' })

    expect(within(group).getByRole('button', { name: 'Livro' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )

    await user.click(within(group).getByRole('button', { name: 'Quadrinhos' }))

    expect(within(group).getByRole('button', { name: 'Quadrinhos' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
    expect(within(group).getByRole('button', { name: 'Livro' })).toHaveAttribute(
      'aria-pressed',
      'false',
    )
  })
})
