import { screen, waitFor } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { tokenStorage } from '../lib/api'
import { API, user } from '../test/fixtures'
import { renderApp } from '../test/render'
import { server } from '../test/server'

const profile = {
  ...user,
  bio: 'Leitora de mangás',
  avatar_url: 'https://exemplo.com/eu.png',
  cover_url: 'https://exemplo.com/capa.jpg',
}

function signInAs(current = user) {
  tokenStorage.set('token-123')
  server.use(
    http.get(`${API}/auth/me`, () => HttpResponse.json(current)),
    http.get(`${API}/lists`, () => HttpResponse.json([])),
  )
}

describe('editar perfil', () => {
  it('mostra a bio no perfil e o atalho para editar', async () => {
    signInAs(profile)
    renderApp('/perfil')

    expect(await screen.findByText('Leitora de mangás')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Editar perfil' })).toHaveAttribute(
      'href',
      '/perfil/editar',
    )
  })

  it('exige login', async () => {
    renderApp('/perfil/editar')

    expect(await screen.findByRole('heading', { name: 'Bem-vinda de volta' })).toBeInTheDocument()
  })

  it('salva bio, avatar e capa e volta ao perfil atualizado', async () => {
    signInAs()
    let sent: unknown
    server.use(
      http.put(`${API}/auth/me`, async ({ request }) => {
        sent = await request.json()
        return HttpResponse.json(profile)
      }),
    )
    const { user: events } = renderApp('/perfil/editar')

    await events.type(await screen.findByLabelText('Avatar (link da imagem)'), profile.avatar_url)
    await events.type(screen.getByLabelText('Capa (link da imagem)'), profile.cover_url)
    await events.type(screen.getByLabelText('Bio'), profile.bio)
    await events.click(screen.getByRole('button', { name: 'Salvar perfil' }))

    await waitFor(() =>
      expect(sent).toEqual({
        bio: profile.bio,
        avatar_url: profile.avatar_url,
        cover_url: profile.cover_url,
      }),
    )
    expect(await screen.findByText('Leitora de mangás')).toBeInTheDocument()
  })

  it('recusa link de imagem sem http e não chama a API', async () => {
    signInAs()
    let called = false
    server.use(
      http.put(`${API}/auth/me`, () => {
        called = true
        return HttpResponse.json(profile)
      }),
    )
    const { user: events } = renderApp('/perfil/editar')

    await events.type(await screen.findByLabelText('Avatar (link da imagem)'), 'minha-foto.png')
    await events.click(screen.getByRole('button', { name: 'Salvar perfil' }))

    expect(await screen.findByText(/comece com http/)).toBeInTheDocument()
    expect(called).toBe(false)
  })

  it('mostra o erro devolvido pela API', async () => {
    signInAs()
    server.use(
      http.put(`${API}/auth/me`, () =>
        HttpResponse.json({ detail: 'A bio deve ter no máximo 300 caracteres' }, { status: 422 }),
      ),
    )
    const { user: events } = renderApp('/perfil/editar')

    await events.type(await screen.findByLabelText('Bio'), 'texto')
    await events.click(screen.getByRole('button', { name: 'Salvar perfil' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('no máximo 300')
  })
})
