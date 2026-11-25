import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'
import { API } from './fixtures'

export const server = setupServer(
  http.get(`${API}/votes/favorites`, () => HttpResponse.json([])),
  http.get(`${API}/notifications`, () => HttpResponse.json({ items: [], unread: 0 })),
)
