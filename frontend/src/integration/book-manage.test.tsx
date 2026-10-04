import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('editar obra', () => {
  it('abre o formulário preenchido com os dados da obra', async () => {
    server.use(http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)))
    signIn()
    renderApp('/livros/1/editar')

    expect(await screen.findByRole('heading', { name: 'Editar obra' })).toBeInTheDocument()
    expect(screen.getByLabelText('Título')).toHaveValue('One Piece, Vol. 1')
    expect(screen.getByLabelText('Autores')).toHaveValue('Eiichiro Oda')
    expect(screen.getByLabelText('ISBN')).toHaveValue('9788542603835')
    expect(screen.getByLabelText('Gêneros')).toHaveValue('Aventura')
    expect(screen.getByRole('button', { name: 'Mangá' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('envia PUT com os dados alterados e volta ao detalhe', async () => {
    let body: unknown
    let current = onePiece
    server.use(
      http.get(`${API}/books/1`, () => HttpResponse.json(current)),
      http.put(`${API}/books/1`, async ({ request }) => {
        body = await request.json()
        current = { ...onePiece, title: 'One Piece 2' }
        return HttpResponse.json(current)
      }),
    )
    signIn()
    const { user } = renderApp('/livros/1/editar')
    const title = await screen.findByLabelText('Título')

    await user.clear(title)
    await user.type(title, 'One Piece 2')
    await user.click(screen.getByRole('button', { name: 'Salvar alterações' }))

    expect(await screen.findByRole('heading', { name: 'One Piece 2' })).toBeInTheDocument()
    expect(body).toMatchObject({ title: 'One Piece 2', genre: ['Mangá', 'Aventura'] })
  })

  it('mostra o erro quando o ISBN já pertence a outra obra', async () => {
    server.use(
      http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
      http.put(`${API}/books/1`, () =>
        HttpResponse.json({ detail: 'ISBN já cadastrado' }, { status: 409 }),
      ),
    )
    signIn()
    const { user } = renderApp('/livros/1/editar')

    await user.click(await screen.findByRole('button', { name: 'Salvar alterações' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('ISBN já cadastrado')
  })

  it('mostra o erro quando a obra não existe', async () => {
    server.use(
      http.get(`${API}/books/9`, () =>
        HttpResponse.json({ detail: 'Livro 9 não encontrado.' }, { status: 404 }),
      ),
    )
    signIn()
    renderApp('/livros/9/editar')

    expect(await screen.findByRole('alert')).toHaveTextContent('Livro 9 não encontrado.')
  })

  it('exige login', async () => {
    renderApp('/livros/1/editar')

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
  })
})

describe('excluir obra', () => {
  beforeEach(() => {
    server.use(http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)))
  })

  it('não mostra editar nem excluir para visitantes', async () => {
    renderApp('/livros/1')

    await screen.findByRole('heading', { name: 'One Piece, Vol. 1' })
    expect(screen.queryByRole('link', { name: 'Editar' })).toBeNull()
    expect(screen.queryByRole('button', { name: 'Excluir' })).toBeNull()
  })

  it('mostra editar e excluir para quem está logado', async () => {
    signIn()
    renderApp('/livros/1')

    expect(await screen.findByRole('link', { name: 'Editar' })).toHaveAttribute(
      'href',
      '/livros/1/editar',
    )
    expect(screen.getByRole('button', { name: 'Excluir' })).toBeInTheDocument()
  })

  it('pede confirmação e permite cancelar sem excluir', async () => {
    signIn()
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('button', { name: 'Excluir' }))
    expect(screen.getByRole('alertdialog')).toHaveTextContent('Essa ação não pode ser desfeita')

    await user.click(screen.getByRole('button', { name: 'Cancelar' }))

    expect(screen.queryByRole('alertdialog')).toBeNull()
    expect(screen.getByRole('button', { name: 'Excluir' })).toBeInTheDocument()
  })

  it('exclui depois de confirmar e volta para a estante', async () => {
    let deleted = false
    server.use(
      http.delete(`${API}/books/1`, () => {
        deleted = true
        return new HttpResponse(null, { status: 204 })
      }),
      http.get(`${API}/books`, () => HttpResponse.json([])),
    )
    signIn()
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('button', { name: 'Excluir' }))
    await user.click(screen.getByRole('button', { name: 'Confirmar exclusão' }))

    expect(await screen.findByText(/Nenhuma obra encontrada/)).toBeInTheDocument()
    await waitFor(() => expect(deleted).toBe(true))
  })

  it('mostra o erro se a exclusão falhar', async () => {
    server.use(
      http.delete(`${API}/books/1`, () =>
        HttpResponse.json({ detail: 'Sessão inválida ou expirada.' }, { status: 401 }),
      ),
    )
    signIn()
    const { user } = renderApp('/livros/1')

    await user.click(await screen.findByRole('button', { name: 'Excluir' }))
    await user.click(screen.getByRole('button', { name: 'Confirmar exclusão' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Sessão inválida ou expirada.')
    expect(screen.getByRole('button', { name: 'Confirmar exclusão' })).toBeEnabled()
  })
})
