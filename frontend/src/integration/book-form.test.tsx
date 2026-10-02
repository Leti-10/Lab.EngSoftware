import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, onePiece } from '../test/fixtures'
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

  it('envia o payload correto (tipo Mangá entra nos gêneros) e confirma o cadastro', async () => {
    let body: unknown
    server.use(
      http.post(`${API}/books`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(onePiece, { status: 201 })
      }),
    )
    signIn()
    const { user } = renderApp('/livros/novo')
    await screen.findByRole('heading', { name: 'Cadastrar obra' })

    await user.click(screen.getByRole('button', { name: 'Mangá' }))
    await fill(user)
    await user.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByRole('status')).toHaveTextContent('foi adicionado à estante')
    expect(body).toEqual({
      isbn: '9788542603835',
      title: 'One Piece, Vol. 1',
      publisher: 'Panini',
      authors: ['Eiichiro Oda', 'Outro Autor'],
      genre: ['Mangá', 'Aventura', 'Shounen'],
      theme: ['Amizade'],
    })
    expect(screen.getByLabelText('Título')).toHaveValue('')
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

    expect(screen.getByRole('button', { name: 'Livro' })).toHaveAttribute('aria-pressed', 'true')

    await user.click(screen.getByRole('button', { name: 'Quadrinhos' }))

    expect(screen.getByRole('button', { name: 'Quadrinhos' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
    expect(screen.getByRole('button', { name: 'Livro' })).toHaveAttribute('aria-pressed', 'false')
  })
})
