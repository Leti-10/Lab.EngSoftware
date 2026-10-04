import { SearchX } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui'

export function NotFoundPage() {
  return (
    <section className="py-20 text-center">
      <SearchX aria-hidden="true" className="mx-auto size-12 text-blue-warm-500" />
      <h1 className="mt-6 text-3xl font-semibold">Página não encontrada</h1>
      <p className="mx-auto mt-3 max-w-md text-ink-soft">
        O endereço que você tentou abrir não existe ou foi movido.
      </p>
      <Link to="/" className="mt-8 inline-block">
        <Button>Voltar para o início</Button>
      </Link>
    </section>
  )
}
