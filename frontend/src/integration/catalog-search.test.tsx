import { fireEvent, screen, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import type { CatalogBook } from '../lib/types'
import { API, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

const jogosVorazes: CatalogBook = {
  isbn: '9788532524935',
  title: 'Jogos Vorazes',
  authors: ['Suzanne Collins'],
  publisher: 'Rocco',
  genres: ['Ficção', 'Aventura'],
  cover_url: 'https://covers.openlibrary.org/b/id/1-M.jpg',
}
const semDados: CatalogBook = {
  isbn: '9788579272998',
  title: 'Outro Livro',
  authors: [],
  publisher: '',
  genres: [],
  cover_url: null,
}
const manga: CatalogBook = {
  isbn: '9781569319017',
  title: 'One Piece, Vol. 1',
  authors: ['Eiichiro Oda'],
  publisher: 'Shonen Jump',
  genres: ['Mangá', 'Aventura'],
  cover_url: null,
}

async function openForm() {
  signIn()
  const view = renderApp('/livros/novo')
  await screen.findByRole('heading', { name: 'Cadastrar obra' })
  return view
}

async function search(user: Awaited<ReturnType<typeof openForm>>['user'], text = 'jogos vorazes') {
  await user.type(screen.getByLabelText('Buscar livro por título, autor ou ISBN'), text)
  await user.click(screen.getByRole('button', { name: 'Buscar' }))
}

describe('busca de livros no cadastro de obra', () => {
  it('aparece no cadastro de obra', async () => {
    await openForm()

    expect(screen.getByRole('heading', { name: 'Buscar livro' })).toBeInTheDocument()
    expect(screen.getByRole('search')).toBeInTheDocument()
  })

  it('não aparece na edição de uma obra', async () => {
    server.use(http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)))
    signIn()
    renderApp('/livros/1/editar')

    await screen.findByRole('heading', { name: 'Editar obra' })
    expect(screen.queryByRole('heading', { name: 'Buscar livro' })).toBeNull()
  })

  it('envia a busca ao backend e lista os resultados', async () => {
    let query: string | null = null
    server.use(
      http.get(`${API}/catalog/search`, ({ request }) => {
        query = new URL(request.url).searchParams.get('q')
        return HttpResponse.json([jogosVorazes, semDados])
      }),
    )
    const { user } = await openForm()

    await search(user)

    const list = await screen.findByRole('list', { name: 'Resultados da busca' })
    expect(query).toBe('jogos vorazes')
    expect(within(list).getByText('Jogos Vorazes')).toBeInTheDocument()
    expect(within(list).getByText('Suzanne Collins')).toBeInTheDocument()
    expect(within(list).getByText('Rocco · ISBN 9788532524935')).toBeInTheDocument()
    expect(within(list).getByText('Autor não informado')).toBeInTheDocument()
  })

  it('preenche o formulário ao escolher um resultado', async () => {
    server.use(http.get(`${API}/catalog/search`, () => HttpResponse.json([jogosVorazes])))
    const { user } = await openForm()
    await search(user)

    await user.click(await screen.findByRole('button', { name: 'Usar Jogos Vorazes' }))

    expect(screen.getByLabelText('Título')).toHaveValue('Jogos Vorazes')
    expect(screen.getByLabelText('Autores')).toHaveValue('Suzanne Collins')
    expect(screen.getByLabelText('ISBN')).toHaveValue('9788532524935')
    expect(screen.getByLabelText('Editora')).toHaveValue('Rocco')
    expect(screen.getByLabelText('Gêneros')).toHaveValue('Ficção, Aventura')
    expect(screen.getByRole('status')).toHaveTextContent('Dados de “Jogos Vorazes” preenchidos')
    expect(screen.queryByRole('list', { name: 'Resultados da busca' })).toBeNull()
  })

  it('marca o tipo Mangá quando os gêneros indicam mangá', async () => {
    server.use(http.get(`${API}/catalog/search`, () => HttpResponse.json([manga])))
    const { user } = await openForm()
    await search(user, 'one piece')

    await user.click(await screen.findByRole('button', { name: 'Usar One Piece, Vol. 1' }))

    expect(screen.getByRole('button', { name: 'Mangá' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('permite cadastrar a obra preenchida pela busca', async () => {
    let body: unknown
    server.use(
      http.get(`${API}/catalog/search`, () => HttpResponse.json([jogosVorazes])),
      http.post(`${API}/books`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json({ ...onePiece, id: 7, title: 'Jogos Vorazes' }, { status: 201 })
      }),
      http.get(`${API}/books/7`, () =>
        HttpResponse.json({ ...onePiece, id: 7, title: 'Jogos Vorazes' }),
      ),
    )
    const { user } = await openForm()
    await search(user)
    await user.click(await screen.findByRole('button', { name: 'Usar Jogos Vorazes' }))

    await user.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByRole('heading', { name: 'Jogos Vorazes' })).toBeInTheDocument()
    expect(body).toMatchObject({
      isbn: '9788532524935',
      title: 'Jogos Vorazes',
      authors: ['Suzanne Collins'],
      publisher: 'Rocco',
      genre: ['Ficção', 'Aventura'],
    })
  })

  it('avisa quando nada é encontrado', async () => {
    server.use(http.get(`${API}/catalog/search`, () => HttpResponse.json([])))
    const { user } = await openForm()

    await search(user, 'xyzxyz')

    expect(await screen.findByText(/Nenhum livro encontrado/)).toBeInTheDocument()
  })

  it('mostra o erro quando a fonte externa está indisponível', async () => {
    server.use(
      http.get(`${API}/catalog/search`, () =>
        HttpResponse.json(
          { detail: 'A busca de livros está indisponível no momento. Tente novamente.' },
          { status: 502 },
        ),
      ),
    )
    const { user } = await openForm()

    await search(user)

    expect(await screen.findByRole('alert')).toHaveTextContent('indisponível no momento')
    expect(screen.getByLabelText('Título')).toBeInTheDocument()
  })

  it('pede ao menos 2 caracteres sem chamar o backend', async () => {
    const { user } = await openForm()

    await search(user, 'a')

    expect(await screen.findByRole('alert')).toHaveTextContent('Digite ao menos 2 caracteres')
  })

  it('troca a capa quebrada pela inicial do título', async () => {
    server.use(http.get(`${API}/catalog/search`, () => HttpResponse.json([jogosVorazes])))
    const { user } = await openForm()
    await search(user)
    const list = await screen.findByRole('list', { name: 'Resultados da busca' })

    fireEvent.error(list.querySelector('img') as HTMLImageElement)

    expect(list.querySelector('img')).toBeNull()
    expect(within(list).getByText('J')).toBeInTheDocument()
  })

  it('mostra a inicial quando a obra não tem capa', async () => {
    server.use(http.get(`${API}/catalog/search`, () => HttpResponse.json([semDados])))
    const { user } = await openForm()

    await search(user, 'outro')

    const list = await screen.findByRole('list', { name: 'Resultados da busca' })
    expect(list.querySelector('img')).toBeNull()
    expect(within(list).getByText('O')).toBeInTheDocument()
  })
})
