import { screen, waitFor, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { API, onePiece, review } from '../test/fixtures'
import { renderApp } from '../test/render'
import { server } from '../test/server'

describe('página de resenhas', () => {
  it('lista resenhas, alterna a posição da capa e abre o livro', async () => {
    server.use(
      http.get(`${API}/reviews/feed`, () =>
        HttpResponse.json({
          items: [
            { ...review, book_title: onePiece.title, book_isbn: onePiece.isbn },
            {
              ...review,
              id: 11,
              comment: 'Uma segunda resenha',
              book_title: 'Outro livro',
              book_isbn: '9788535902778',
            },
          ],
          total: 2,
          page: 1,
          page_size: 30,
        }),
      ),
      http.get(`${API}/books/1`, () => HttpResponse.json(onePiece)),
      http.get(`${API}/reviews`, () => HttpResponse.json([])),
      http.get(`${API}/books`, () => HttpResponse.json([])),
    )
    const { user } = renderApp('/resenhas')

    const first = await screen.findByRole('link', { name: /Resenha de bia sobre One Piece/ })
    const second = screen.getByRole('link', { name: /Resenha de bia sobre Outro livro/ })

    expect(first).toHaveAttribute('href', '/livros/1')
    expect(within(first).getByText('Uma aventura incrível')).toBeInTheDocument()
    expect(within(first).getByText('2 curtidas')).toBeInTheDocument()
    expect(within(first).getByAltText('Capa de One Piece, Vol. 1')).toBeInTheDocument()
    expect(first).toHaveClass('flex-row')
    expect(second).toHaveClass('flex-row-reverse')

    await user.click(first)

    expect(await screen.findByRole('heading', { name: onePiece.title })).toBeInTheDocument()
  })

  it('busca outras páginas somente após clique e permite ordenar por curtidas', async () => {
    const requestedPages: string[] = []
    server.use(
      http.get(`${API}/reviews/feed`, ({ request }) => {
        const url = new URL(request.url)
        const page = url.searchParams.get('page')
        const sort = url.searchParams.get('sort')
        requestedPages.push(`page=${page}&sort=${sort}`)
        return HttpResponse.json({
          items:
            page === '2'
              ? [
                  {
                    ...review,
                    id: 12,
                    comment: 'Resenha da página 2',
                    book_title: onePiece.title,
                    book_isbn: onePiece.isbn,
                  },
                ]
              : [],
          total: 61,
          page: Number(page),
          page_size: 30,
        })
      }),
    )
    const { user } = renderApp('/resenhas')

    const pagination = await screen.findByRole('navigation', {
      name: 'Paginação das resenhas',
    })
    expect(requestedPages).toEqual(['page=1&sort=recent'])
    expect(within(pagination).getByRole('button', { name: 'Página 3' })).toBeInTheDocument()

    await user.selectOptions(screen.getByLabelText('Ordenar resenhas'), 'popular')
    await waitFor(() => {
      expect(requestedPages).toEqual(['page=1&sort=recent', 'page=1&sort=popular'])
    })
    await screen.findByRole('button', { name: 'Página 2' })

    await user.click(screen.getByRole('button', { name: 'Página 2' }))

    expect(await screen.findByText('Resenha da página 2')).toBeInTheDocument()
    expect(requestedPages).toEqual([
      'page=1&sort=recent',
      'page=1&sort=popular',
      'page=2&sort=popular',
    ])
  })
})
