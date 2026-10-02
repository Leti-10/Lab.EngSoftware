import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Alert, Button, Card, Field } from './ui'

describe('Button', () => {
  it('dispara onClick', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Salvar</Button>)

    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))

    expect(onClick).toHaveBeenCalledOnce()
  })

  it('não dispara quando desabilitado', async () => {
    const onClick = vi.fn()
    render(
      <Button disabled onClick={onClick}>
        Salvar
      </Button>,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))

    expect(onClick).not.toHaveBeenCalled()
  })

  it('aplica estilos diferentes por variante', () => {
    render(
      <>
        <Button>Primário</Button>
        <Button variant="ghost">Fantasma</Button>
      </>,
    )

    expect(screen.getByText('Primário')).toHaveClass('bg-blue-warm-600')
    expect(screen.getByText('Fantasma')).not.toHaveClass('bg-blue-warm-600')
  })
})

describe('Field', () => {
  it('associa o rótulo ao campo', async () => {
    render(<Field label="E-mail" />)

    await userEvent.type(screen.getByLabelText('E-mail'), 'ana@example.com')

    expect(screen.getByLabelText('E-mail')).toHaveValue('ana@example.com')
  })

  it('mostra a dica quando informada', () => {
    render(<Field label="Senha" hint="Mínimo de 6 caracteres." />)

    expect(screen.getByText('Mínimo de 6 caracteres.')).toBeInTheDocument()
  })

  it('repassa atributos nativos ao input', () => {
    render(<Field label="Senha" type="password" required minLength={6} />)

    const input = screen.getByLabelText('Senha')
    expect(input).toHaveAttribute('type', 'password')
    expect(input).toBeRequired()
    expect(input).toHaveAttribute('minlength', '6')
  })
})

describe('Card e Alert', () => {
  it('Card renderiza o conteúdo', () => {
    render(<Card>conteúdo</Card>)

    expect(screen.getByText('conteúdo')).toBeInTheDocument()
  })

  it('Alert usa role="alert" para leitores de tela', () => {
    render(<Alert>Algo deu errado</Alert>)

    expect(screen.getByRole('alert')).toHaveTextContent('Algo deu errado')
  })
})
