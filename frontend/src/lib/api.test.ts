import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { API } from '../test/fixtures'
import { ApiError, api, clearLegacyAuthToken } from './api'

async function failure(promise: Promise<unknown>): Promise<ApiError> {
  try {
    await promise
  } catch (error) {
    return error as ApiError
  }
  throw new Error('esperava que a chamada falhasse')
}

describe('autenticação por cookie', () => {
  it('remove o token legado do localStorage', () => {
    localStorage.setItem('estante.token', 'jwt-legado')

    clearLegacyAuthToken()

    expect(localStorage.getItem('estante.token')).toBeNull()
  })
})

describe('api', () => {
  it('devolve o JSON em caso de sucesso', async () => {
    server.use(http.get(`${API}/books`, () => HttpResponse.json([{ id: 1 }])))

    await expect(api('/books')).resolves.toEqual([{ id: 1 }])
  })

  it('envia cookies e não envia Authorization', async () => {
    let auth: string | null = null
    let credentials: RequestCredentials | undefined
    server.use(
      http.get(`${API}/auth/me`, ({ request }) => {
        auth = request.headers.get('Authorization')
        credentials = request.credentials
        return HttpResponse.json({})
      }),
    )

    await api('/auth/me')

    expect(auth).toBeNull()
    expect(credentials).toBe('include')
  })

  it('define Content-Type JSON quando há corpo', async () => {
    let contentType: string | null = null
    server.use(
      http.post(`${API}/books`, ({ request }) => {
        contentType = request.headers.get('Content-Type')
        return HttpResponse.json({}, { status: 201 })
      }),
    )

    await api('/books', { method: 'POST', body: JSON.stringify({ a: 1 }) })

    expect(contentType).toBe('application/json')
  })

  it('devolve null em respostas 204', async () => {
    server.use(http.delete(`${API}/x`, () => new HttpResponse(null, { status: 204 })))

    await expect(api('/x', { method: 'DELETE' })).resolves.toBeNull()
  })

  it('usa a mensagem de detail (string) como erro', async () => {
    server.use(
      http.post(`${API}/auth/login`, () =>
        HttpResponse.json({ detail: 'E-mail ou senha inválidos.' }, { status: 401 }),
      ),
    )

    const error = await failure(api('/auth/login', { method: 'POST', body: '{}' }))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(401)
    expect(error.message).toBe('E-mail ou senha inválidos.')
  })

  it('formata erros de validação do Pydantic (detail em lista)', async () => {
    server.use(
      http.post(`${API}/books`, () =>
        HttpResponse.json(
          { detail: [{ loc: ['body', 'isbn'], msg: 'Field required' }] },
          { status: 422 },
        ),
      ),
    )

    const error = await failure(api('/books', { method: 'POST', body: '{}' }))

    expect(error.message).toBe('isbn: Field required')
    expect(error.status).toBe(422)
  })

  it('usa mensagem genérica quando o corpo do erro não ajuda', async () => {
    server.use(http.get(`${API}/books`, () => new HttpResponse('boom', { status: 500 })))

    const error = await failure(api('/books'))

    expect(error.status).toBe(500)
    expect(error.message).toBe('Algo deu errado. Tente novamente.')
  })

  it('converte falha de rede em ApiError com status 0', async () => {
    server.use(http.get(`${API}/books`, () => HttpResponse.error()))

    const error = await failure(api('/books'))

    expect(error).toBeInstanceOf(ApiError)
    expect(error.status).toBe(0)
    expect(error.message).toBe('Não foi possível conectar ao servidor.')
  })

  it('propaga o cancelamento (AbortError) sem converter', async () => {
    server.use(http.get(`${API}/books`, () => HttpResponse.json([])))
    const controller = new AbortController()
    controller.abort()

    const error = await failure(api('/books', { signal: controller.signal }))

    expect(error.name).toBe('AbortError')
  })
})
