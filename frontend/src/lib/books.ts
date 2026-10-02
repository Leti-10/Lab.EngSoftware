export const KINDS = ['Livro', 'Mangá', 'Quadrinhos'] as const
export type Kind = (typeof KINDS)[number]

export function kindOf(genre: string[]): Kind {
  return KINDS.find((kind) => kind !== 'Livro' && genre.includes(kind)) ?? 'Livro'
}

export function splitList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}
