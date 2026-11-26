import { useEffect, useRef } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { titleFor, useDocumentTitle } from '../lib/pageTitle'
import { Alert } from './ui'
import { Navbar } from './Navbar'

export function Layout() {
  const { user, favoritesError } = useAuth()
  const { pathname } = useLocation()
  const main = useRef<HTMLElement>(null)
  const firstRender = useRef(true)

  useDocumentTitle(titleFor(pathname))

  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false
      return
    }
    main.current?.focus({ preventScroll: true })
    window.scrollTo(0, 0)
  }, [pathname])

  return (
    <div className="min-h-screen">
      <a
        href="#conteudo"
        className="sr-only rounded-full bg-blue-warm-600 px-4 py-2 text-sm font-medium text-cream-50 focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-30"
      >
        Pular para o conteúdo
      </a>
      <Navbar />
      <main
        id="conteudo"
        ref={main}
        tabIndex={-1}
        className="mx-auto max-w-5xl px-5 py-10 focus:outline-none"
      >
        {user && favoritesError && (
          <div className="mb-6">
            <Alert>{favoritesError}</Alert>
          </div>
        )}
        <Outlet />
      </main>
    </div>
  )
}
