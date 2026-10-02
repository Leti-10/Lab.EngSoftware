import { screen, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, domCasmurro, favoritos, onePiece } from '../test/fixtures'
import { renderApp, signIn } from '../test/render'
import { server } from '../test/server'

describe('minhas listas', () => {
  it('lista as listas da pessoa com contagem de obras e marcação de privada', async () => {
    server.use(
      http.get(`${API}/lists`, () =>
        HttpResponse.json([
          { ...favoritos, books: [onePiece, domCasmurro] },
          { ...favoritos, id: 2, name: 'Segredo', private: true, books: [onePiece] },
        ]),
      ),
    )
    signIn()
    renderApp('/listas')

    expect(await screen.findByText('Favoritos')).toBeInTheDocument()
    expect(screen.getByText('2 obras')).toBeInTheDocument()
    expect(screen.getByText('1 obra')).toBeInTheDocument()
    expect(screen.getByText('Privada')).toBeInTheDocument()
  })

  it('mostra mensagem quando não há listas', async () => {
    server.use(http.get(`${API}/lists`, () => HttpResponse.json([])))
    signIn()
    renderApp('/listas')

    expect(await screen.findByText(/ainda não criou nenhuma lista/)).toBeInTheDocument()
  })

  it('cria uma lista, mostra na tela e limpa o formulário', async () => {
    let body: unknown
    server.use(
      http.get(`${API}/lists`, () => HttpResponse.json([])),
      http.post(`${API}/lists`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json(favoritos, { status: 201 })
      }),
    )
    signIn()
    const { user } = renderApp('/listas')
    await screen.findByText(/ainda não criou nenhuma lista/)

    await user.type(screen.getByLabelText('Nome'), 'Favoritos')
    await user.type(screen.getByLabelText('Descrição'), 'Os que eu mais amo')
    await user.click(screen.getByLabelText('Lista privada'))
    await user.click(screen.getByRole('button', { name: 'Criar lista' }))

    expect(await screen.findByText('Os que eu mais amo', { selector: 'p' })).toBeInTheDocument()
    expect(body).toEqual({ name: 'Favoritos', description: 'Os que eu mais amo', private: true })
    expect(screen.getByLabelText('Nome')).toHaveValue('')
  })

  it('mostra erro de nome duplicado (409)', async () => {
    server.use(
      http.get(`${API}/lists`, () => HttpResponse.json([])),
      http.post(`${API}/lists`, () =>
        HttpResponse.json({ detail: 'Nome da lista já cadastrado' }, { status: 409 }),
      ),
    )
    signIn()
    const { user } = renderApp('/listas')
    await screen.findByText(/ainda não criou nenhuma lista/)

    await user.type(screen.getByLabelText('Nome'), 'Favoritos')
    await user.type(screen.getByLabelText('Descrição'), 'Qualquer')
    await user.click(screen.getByRole('button', { name: 'Criar lista' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Nome da lista já cadastrado')
  })

  it('exige login', async () => {
    renderApp('/listas')

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
  })
})

describe('detalhe da lista', () => {
  it('mostra as obras da lista e só oferece as que ainda não estão nela', async () => {
    server.use(
      http.get(`${API}/lists/1`, () => HttpResponse.json({ ...favoritos, books: [onePiece] })),
      http.get(`${API}/books`, () => HttpResponse.json([onePiece, domCasmurro])),
    )
    signIn()
    renderApp('/listas/1')

    expect(await screen.findByRole('heading', { name: 'Favoritos' })).toBeInTheDocument()
    expect(screen.getByText('One Piece, Vol. 1', { selector: 'p' })).toBeInTheDocument()

    const select = screen.getByLabelText('Escolher obra para adicionar')
    const options = within(select)
      .getAllByRole('option')
      .map((o) => o.textContent)
    expect(options).toEqual(['Adicionar obra…', 'Dom Casmurro'])
  })

  it('mostra lista vazia', async () => {
    server.use(
      http.get(`${API}/lists/1`, () => HttpResponse.json(favoritos)),
      http.get(`${API}/books`, () => HttpResponse.json([])),
    )
    signIn()
    renderApp('/listas/1')

    expect(await screen.findByText('Esta lista ainda está vazia.')).toBeInTheDocument()
  })

  it('adiciona uma obra à lista', async () => {
    let body: unknown
    server.use(
      http.get(`${API}/lists/1`, () => HttpResponse.json(favoritos)),
      http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
      http.post(`${API}/lists/1/books`, async ({ request }) => {
        body = await request.json()
        return HttpResponse.json({ ...favoritos, books: [onePiece] })
      }),
    )
    signIn()
    const { user } = renderApp('/listas/1')
    const select = await screen.findByLabelText('Escolher obra para adicionar')
    await user.selectOptions(select, 'One Piece, Vol. 1')

    await user.click(screen.getByRole('button', { name: 'Adicionar' }))

    expect(await screen.findByText('Eiichiro Oda')).toBeInTheDocument()
    expect(body).toEqual({ book_id: 1 })
    expect(screen.queryByText('Esta lista ainda está vazia.')).toBeNull()
  })

  it('só habilita "Adicionar" depois de escolher uma obra', async () => {
    server.use(
      http.get(`${API}/lists/1`, () => HttpResponse.json(favoritos)),
      http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
    )
    signIn()
    const { user } = renderApp('/listas/1')
    const select = await screen.findByLabelText('Escolher obra para adicionar')

    expect(screen.getByRole('button', { name: 'Adicionar' })).toBeDisabled()

    await user.selectOptions(select, 'One Piece, Vol. 1')

    expect(screen.getByRole('button', { name: 'Adicionar' })).toBeEnabled()
  })

  it('mostra erro ao tentar adicionar obra repetida (409)', async () => {
    server.use(
      http.get(`${API}/lists/1`, () => HttpResponse.json(favoritos)),
      http.get(`${API}/books`, () => HttpResponse.json([onePiece])),
      http.post(`${API}/lists/1/books`, () =>
        HttpResponse.json({ detail: 'Este livro já está na lista.' }, { status: 409 }),
      ),
    )
    signIn()
    const { user } = renderApp('/listas/1')
    await user.selectOptions(await screen.findByLabelText('Escolher obra para adicionar'), '1')

    await user.click(screen.getByRole('button', { name: 'Adicionar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Este livro já está na lista.')
  })

  it('mostra "Lista não encontrada" para 404', async () => {
    server.use(
      http.get(`${API}/lists/9`, () => HttpResponse.json({ detail: 'x' }, { status: 404 })),
      http.get(`${API}/books`, () => HttpResponse.json([])),
    )
    signIn()
    renderApp('/listas/9')

    expect(await screen.findByRole('alert')).toHaveTextContent('Lista não encontrada.')
  })
})
