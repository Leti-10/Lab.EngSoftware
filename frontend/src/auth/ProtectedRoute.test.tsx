import { render, screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { tokenStorage } from '../lib/api'
import { API } from '../test/fixtures'
import { server } from '../test/server'
import { AuthProvider } from './AuthContext'
import { ProtectedRoute } from './ProtectedRoute'

function renderProtected() {
  return render(
    <MemoryRouter initialEntries={['/segredo']}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<p>tela de login</p>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/segredo" element={<p>conteúdo protegido</p>} />
          </Route>
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  it('redireciona visitantes para o login', async () => {
    renderProtected()

    expect(await screen.findByText('tela de login')).toBeInTheDocument()
  })

  it('mostra o conteúdo para quem está logado', async () => {
    tokenStorage.set('token-123')
    server.use(
      http.get(`${API}/auth/me`, () =>
        HttpResponse.json({ id: 1, username: 'ana', email: 'ana@example.com', role: 'user' }),
      ),
    )
    renderProtected()

    expect(await screen.findByText('conteúdo protegido')).toBeInTheDocument()
  })

  it('mostra carregando enquanto valida o token salvo', () => {
    tokenStorage.set('token-123')
    server.use(http.get(`${API}/auth/me`, () => new Promise(() => {})))
    renderProtected()

    expect(screen.getByText('Carregando…')).toBeInTheDocument()
  })
})
