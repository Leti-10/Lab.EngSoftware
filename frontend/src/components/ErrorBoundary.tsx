import { TriangleAlert } from 'lucide-react'
import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { Button } from './ui'

interface State {
  failed: boolean
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { failed: false }

  static getDerivedStateFromError(): State {
    return { failed: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error(error, info.componentStack)
  }

  render() {
    if (!this.state.failed) return this.props.children

    return (
      <section role="alert" className="mx-auto max-w-md px-5 py-24 text-center">
        <TriangleAlert aria-hidden="true" className="mx-auto size-12 text-danger" />
        <h1 className="mt-6 font-serif text-3xl font-semibold">Algo deu errado</h1>
        <p className="mt-3 text-ink-soft">
          Encontramos um problema inesperado. Tente recarregar a página.
        </p>
        <Button className="mt-8" onClick={() => window.location.reload()}>
          Recarregar a página
        </Button>
      </section>
    )
  }
}
