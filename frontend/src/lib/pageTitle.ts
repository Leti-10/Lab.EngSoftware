import { useEffect } from 'react'

const SITE = 'Estante'

const TITLES: [RegExp, string][] = [
  [/^\/$/, 'Início'],
  [/^\/login$/, 'Entrar'],
  [/^\/cadastro$/, 'Criar conta'],
  [/^\/livros$/, 'Estante'],
  [/^\/livros\/novo$/, 'Cadastrar obra'],
  [/^\/livros\/[^/]+\/editar$/, 'Editar obra'],
  [/^\/perfil$/, 'Meu perfil'],
  [/^\/perfil\/editar$/, 'Editar perfil'],
  [/^\/listas$/, 'Minhas listas'],
  [/^\/favoritos$/, 'Favoritos'],
  [/^\/feed$/, 'Feed'],
  [/^\/notificacoes$/, 'Notificações'],
  [/^\/recomendacoes$/, 'Recomendações'],
]

export function titleFor(pathname: string): string | null {
  const match = TITLES.find(([pattern]) => pattern.test(pathname))
  return match ? match[1] : null
}

export function formatTitle(title: string) {
  return title === SITE ? SITE : `${title} · ${SITE}`
}

export function useDocumentTitle(title: string | null | undefined) {
  useEffect(() => {
    if (title) document.title = formatTitle(title)
  }, [title])
}
