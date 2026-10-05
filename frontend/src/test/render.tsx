import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { MemoryRouter } from 'react-router-dom'
import { AppRoutes } from '../App'
import { AuthProvider } from '../auth/AuthContext'
import { tokenStorage } from '../lib/api'
import { API, user } from './fixtures'
import { server } from './server'

export function renderApp(route = '/') {
  const events = userEvent.setup()
  const view = render(
    <MemoryRouter initialEntries={[route]}>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </MemoryRouter>,
  )
  return { user: events, ...view }
}

export function signIn() {
  tokenStorage.set('token-123')
  server.use(http.get(`${API}/auth/me`, () => HttpResponse.json(user)))
}
