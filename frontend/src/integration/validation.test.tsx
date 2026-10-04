import { screen } from '@testing-library/react'
import { renderApp, signIn } from '../test/render'

describe('validação do login', () => {
  it('mostra mensagens próprias nos campos vazios, sem chamar a API', async () => {
    const { user } = renderApp('/login')

    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Informe seu e-mail.')).toBeInTheDocument()
    expect(screen.getByText('Informe sua senha.')).toBeInTheDocument()
    expect(screen.getByLabelText('E-mail')).toHaveAttribute('aria-invalid', 'true')
  })

  it('explica quando o e-mail é inválido', async () => {
    const { user } = renderApp('/login')

    await user.type(screen.getByLabelText('E-mail'), 'ana')
    await user.type(screen.getByLabelText('Senha'), 'senha123')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText(/e-mail válido/)).toBeInTheDocument()
  })

  it('limpa o erro do campo quando a pessoa volta a digitar', async () => {
    const { user } = renderApp('/login')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await screen.findByText('Informe sua senha.')

    await user.type(screen.getByLabelText('Senha'), 's')

    expect(screen.queryByText('Informe sua senha.')).toBeNull()
    expect(screen.getByLabelText('Senha')).not.toHaveAttribute('aria-invalid')
  })

  it('mostra um exemplo no campo de senha', () => {
    renderApp('/login')

    expect(screen.getByLabelText('Senha')).toHaveAttribute('placeholder', 'Sua senha')
  })
})

describe('validação do cadastro', () => {
  it('valida todos os campos de uma vez', async () => {
    const { user } = renderApp('/cadastro')

    await user.click(screen.getByRole('button', { name: 'Criar conta' }))

    expect(await screen.findByText('Escolha um nome de usuário.')).toBeInTheDocument()
    expect(screen.getByText('Informe seu e-mail.')).toBeInTheDocument()
    expect(screen.getByText('Crie uma senha.')).toBeInTheDocument()
    expect(screen.getByText('Confirme sua senha.')).toBeInTheDocument()
  })

  it('avisa quando usuário e senha são curtos demais', async () => {
    const { user } = renderApp('/cadastro')

    await user.type(screen.getByLabelText('Nome de usuário'), 'ab')
    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), '123')
    await user.type(screen.getByLabelText('Confirmar senha'), '123')
    await user.click(screen.getByRole('button', { name: 'Criar conta' }))

    expect(await screen.findByText(/nome de usuário deve ter pelo menos 3/)).toBeInTheDocument()
    expect(screen.getByText('A senha deve ter pelo menos 6 caracteres.')).toBeInTheDocument()
  })

  it('mostra exemplos nos campos de senha', () => {
    renderApp('/cadastro')

    expect(screen.getByLabelText('Senha')).toHaveAttribute('placeholder', 'Crie uma senha')
    expect(screen.getByLabelText('Confirmar senha')).toHaveAttribute(
      'placeholder',
      'Repita a senha',
    )
  })
})

describe('validação do cadastro de obra', () => {
  it('exige os campos obrigatórios', async () => {
    signIn()
    const { user } = renderApp('/livros/novo')
    await screen.findByRole('heading', { name: 'Cadastrar obra' })

    await user.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByText('Informe o título da obra.')).toBeInTheDocument()
    expect(screen.getByText('Informe ao menos um autor.')).toBeInTheDocument()
    expect(screen.getByText('Informe o ISBN.')).toBeInTheDocument()
    expect(screen.getByText('Informe a editora.')).toBeInTheDocument()
    expect(screen.getByText('Informe ao menos um gênero.')).toBeInTheDocument()
  })

  it('exige ISBN com pelo menos 10 caracteres', async () => {
    signIn()
    const { user } = renderApp('/livros/novo')
    await screen.findByRole('heading', { name: 'Cadastrar obra' })

    await user.type(screen.getByLabelText('ISBN'), '123')
    await user.click(screen.getByRole('button', { name: 'Cadastrar' }))

    expect(await screen.findByText('O ISBN deve ter pelo menos 10 caracteres.')).toBeInTheDocument()
  })
})

describe('validação da nova lista', () => {
  it('exige nome e descrição', async () => {
    signIn()
    const { user } = renderApp('/listas')
    await screen.findByRole('heading', { name: 'Minhas listas' })

    await user.click(screen.getByRole('button', { name: 'Criar lista' }))

    expect(await screen.findByText('Dê um nome à lista.')).toBeInTheDocument()
    expect(screen.getByText('Escreva uma breve descrição.')).toBeInTheDocument()
  })

  it('exige nome com pelo menos 3 caracteres', async () => {
    signIn()
    const { user } = renderApp('/listas')
    await screen.findByRole('heading', { name: 'Minhas listas' })

    await user.type(screen.getByLabelText('Nome'), 'ab')
    await user.click(screen.getByRole('button', { name: 'Criar lista' }))

    expect(await screen.findByText('O nome deve ter pelo menos 3 caracteres.')).toBeInTheDocument()
  })
})
