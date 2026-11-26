import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { API } from './fixtures'

export const server = setupServer(
  http.get(`${API}/auth/me`, () =>
    HttpResponse.json({ detail: 'Sessão inválida ou expirada.' }, { status: 401 }),
  ),
  http.post(`${API}/auth/logout`, () => new HttpResponse(null, { status: 204 })),
  http.get(`${API}/votes/favorites`, () => HttpResponse.json([])),
  http.get(`${API}/notifications`, () => HttpResponse.json({ items: [], unread: 0 })),
)
