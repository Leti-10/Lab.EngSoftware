import { screen } from '@testing-library/react'
import { renderApp } from '../test/render'

describe('início', () => {
  it('mostra a chamada principal', () => {
    renderApp('/')

    expect(screen.getByRole('heading', { name: /Sua estante/ })).toBeInTheDocument()
  })

  it('mostra o link de início na navbar', () => {
    renderApp('/')

    expect(screen.getByRole('link', { name: 'Início' })).toHaveAttribute('href', '/')
  })
})
