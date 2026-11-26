import { Flag } from 'lucide-react'
import { useEffect, useId, useState } from 'react'
import type { FormEvent, MouseEvent } from 'react'
import { api } from '../lib/api'
import type { Report } from '../lib/types'
import { Alert, Button } from './ui'

interface ReportButtonProps {
  targetId: number
  targetEntity: string
  targetLabel: string
  className?: string
  onSuccess?: () => void
}

export function ReportButton({
  targetId,
  targetEntity,
  targetLabel,
  className = '',
  onSuccess,
}: ReportButtonProps) {
  const titleId = useId()
  const [reporting, setReporting] = useState(false)
  const [description, setDescription] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!reporting) return

    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape' && !submitting) setReporting(false)
    }

    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [reporting, submitting])

  function closeModal() {
    if (submitting) return
    setReporting(false)
  }

  function openModal() {
    setDescription('')
    setError(null)
    setReporting(true)
  }

  function handleBackdropClick(event: MouseEvent<HTMLDivElement>) {
    if (event.target === event.currentTarget) closeModal()
  }

  async function handleReport(event: FormEvent) {
    event.preventDefault()
    const trimmedDescription = description.trim()
    if (!trimmedDescription) {
      setError('Descreva o motivo da denúncia.')
      return
    }

    setError(null)
    setSubmitting(true)
    try {
      await api<Report>('/reports', {
        method: 'POST',
        body: JSON.stringify({
          target_id: targetId,
          target_entity: targetEntity,
          description: trimmedDescription,
        }),
      })
      setReporting(false)
      setDescription('')
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível enviar a denúncia.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={openModal}
        className={`group inline-flex cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-full border border-danger/70 bg-danger/10 px-5 py-2.5 text-sm font-medium text-danger shadow-sm transition-colors hover:bg-danger/15 ${className}`}
      >
        <Flag
          aria-hidden="true"
          className="size-4 shrink-0 text-danger transition-transform duration-200 ease-out group-hover:-translate-y-0.5 group-hover:-rotate-12"
        />
        Reportar
      </button>

      {reporting && (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-ink/30 px-4 backdrop-blur-sm"
          onMouseDown={handleBackdropClick}
        >
          <section
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            className="w-full max-w-md rounded-2xl border border-cream-300 bg-cream-50 p-6 shadow-xl"
          >
            <div className="flex items-start gap-3">
              <span className="grid size-10 shrink-0 place-items-center rounded-full bg-danger/10 text-danger">
                <Flag aria-hidden="true" className="size-5" />
              </span>
              <div>
                <h2 id={titleId} className="text-xl font-semibold text-ink">
                  Reportar conteúdo
                </h2>
                <p className="mt-1 text-sm text-ink-soft">
                  Conte-nos por que <strong className="font-medium text-ink">{targetLabel}</strong>{' '}
                  deve ser analisado.
                </p>
              </div>
            </div>

            <form onSubmit={handleReport} className="mt-5">
              <label
                htmlFor={`${titleId}-description`}
                className="mb-1.5 block text-sm font-medium text-ink"
              >
                Motivo
              </label>
              <textarea
                id={`${titleId}-description`}
                value={description}
                onChange={(event) => {
                  setDescription(event.target.value)
                  setError(null)
                }}
                maxLength={1000}
                rows={5}
                placeholder="Descreva o problema..."
                aria-invalid={error ? true : undefined}
                className="w-full resize-none rounded-xl border border-cream-300 bg-cream-50 px-4 py-3 text-sm text-ink placeholder:text-ink-soft/60 focus:border-blue-warm-500 focus:outline-none"
              />
              <p className="mt-1 text-right text-xs text-ink-soft">{description.length}/1000</p>

              {error && (
                <div className="mt-3">
                  <Alert>{error}</Alert>
                </div>
              )}

              <div className="mt-5 flex justify-end gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  onClick={closeModal}
                  disabled={submitting}
                  className="cursor-pointer"
                >
                  Cancelar
                </Button>
                <button
                  type="submit"
                  disabled={submitting || !description.trim()}
                  className="cursor-pointer rounded-full border border-danger/70 bg-danger px-5 py-2.5 text-sm font-medium text-cream-50 shadow-sm transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {submitting ? 'Enviando…' : 'Enviar denúncia'}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </>
  )
}
