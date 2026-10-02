import { screen } from '@testing-library/react'
import { renderApp, signIn } from '../test/render'

describe('início', () => {
  it('mostra a chamada principal', () => {
    renderApp('/')

    expect(screen.getByRole('heading', { name: /Sua estante/ })).toBeInTheDocument()
  })

  it('leva visitantes à estante e ao cadastro', () => {
    renderApp('/')

    expect(screen.getByRole('link', { name: 'Explorar a estante' })).toHaveAttribute(
      'href',
      '/livros',
    )
    expect(screen.getByRole('link', { name: 'Criar conta' })).toHaveAttribute('href', '/cadastro')
  })

  it('esconde "Criar conta" para quem já está logado', async () => {
    signIn()
    renderApp('/')

    await screen.findByText('Olá, ana')
    expect(screen.queryByRole('link', { name: 'Criar conta' })).toBeNull()
  })
})
