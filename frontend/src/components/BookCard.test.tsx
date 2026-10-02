import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { domCasmurro, onePiece } from '../test/fixtures'
import { BookCard, BookCover, coverUrl } from './BookCard'

describe('BookCard', () => {
  it('mostra título, autores e tipo, e leva ao detalhe', () => {
    render(
      <MemoryRouter>
        <BookCard book={onePiece} />
      </MemoryRouter>,
    )

    expect(screen.getByRole('link')).toHaveAttribute('href', '/livros/1')
    expect(screen.getByText('Eiichiro Oda')).toBeInTheDocument()
    expect(screen.getByText('Mangá')).toBeInTheDocument()
  })

  it('exibe "Livro" quando a obra não é mangá nem quadrinho', () => {
    render(
      <MemoryRouter>
        <BookCard book={domCasmurro} />
      </MemoryRouter>,
    )

    expect(screen.getByText('Livro')).toBeInTheDocument()
  })

  it('junta vários autores', () => {
    render(
      <MemoryRouter>
        <BookCard book={{ ...onePiece, authors: ['A', 'B'] }} />
      </MemoryRouter>,
    )

    expect(screen.getByText('A, B')).toBeInTheDocument()
  })
})

describe('BookCover', () => {
  it('é decorativa para leitores de tela', () => {
    const { container } = render(<BookCover book={onePiece} />)

    expect(container.firstChild).toHaveAttribute('aria-hidden', 'true')
  })

  it('busca a capa pelo ISBN', () => {
    const { container } = render(<BookCover book={onePiece} />)

    expect(container.querySelector('img')).toHaveAttribute('src', coverUrl(onePiece.isbn))
    expect(coverUrl('9788542603835')).toContain('/isbn/9788542603835-M.jpg')
  })

  it('volta para a capa gerada quando a imagem não existe', () => {
    const { container } = render(<BookCover book={onePiece} />)

    fireEvent.error(container.querySelector('img') as HTMLImageElement)

    expect(container.querySelector('img')).toBeNull()
    expect(screen.getByText('One Piece, Vol. 1')).toBeInTheDocument()
  })
})
