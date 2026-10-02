import { useId } from 'react'
import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from 'react'

export function Button({
  variant = 'primary',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' }) {
  const styles =
    variant === 'primary'
      ? 'bg-blue-warm-600 text-cream-50 hover:bg-blue-warm-700'
      : 'text-blue-warm-600 border border-blue-warm-100 hover:bg-blue-warm-50'
  return (
    <button
      className={`inline-flex items-center justify-center rounded-full px-5 py-2.5 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${styles} ${className}`}
      {...props}
    />
  )
}

export function Field({
  label,
  hint,
  id,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label: string; hint?: string }) {
  const generatedId = useId()
  const inputId = id ?? generatedId
  const hintId = `${inputId}-hint`

  return (
    <div>
      <label htmlFor={inputId} className="mb-1.5 block text-sm font-medium text-ink">
        {label}
      </label>
      <input
        id={inputId}
        aria-describedby={hint ? hintId : undefined}
        className="w-full rounded-xl border border-cream-300 bg-cream-50 px-4 py-2.5 text-sm text-ink placeholder:text-ink-soft/60 focus:border-blue-warm-500 focus:outline-none"
        {...props}
      />
      {hint && (
        <span id={hintId} className="mt-1 block text-xs text-ink-soft">
          {hint}
        </span>
      )}
    </div>
  )
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-2xl border border-cream-300 bg-cream-50 p-6 shadow-sm ${className}`}>
      {children}
    </div>
  )
}

export function Alert({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="rounded-xl bg-danger/10 px-4 py-2.5 text-sm text-danger">
      {children}
    </p>
  )
}
