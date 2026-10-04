export type FieldErrors<K extends string> = Partial<Record<K, string>>

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isEmail(value: string) {
  return EMAIL_PATTERN.test(value.trim())
}

export function compact<K extends string>(errors: Record<K, string | undefined>): FieldErrors<K> {
  const result: FieldErrors<K> = {}
  for (const key of Object.keys(errors) as K[]) {
    if (errors[key]) result[key] = errors[key]
  }
  return result
}

export function hasErrors(errors: object) {
  return Object.keys(errors).length > 0
}

export function validateEmail(value: string) {
  if (!value.trim()) return 'Informe seu e-mail.'
  if (!isEmail(value)) return 'Digite um e-mail válido, como voce@email.com.'
  return undefined
}
