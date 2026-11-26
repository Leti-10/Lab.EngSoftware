# Manual de Execução

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [1. Backend](#1-backend)
- [2. Frontend](#2-frontend)
- [3. Usando o app](#3-usando-o-app)
- [Testes e qualidade](#testes-e-qualidade)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Docker](#docker)
- [Notas operacionais](#notas-operacionais)

## Pré-requisitos

| Ferramenta | Versão | Uso |
| --- | --- | --- |
| Python | 3.14 (versão final) | Backend |
| [uv](https://docs.astral.sh/uv/) | recente | Gerenciador de dependências do backend |
| Node.js | 22 ou superior | Frontend |
| PostgreSQL | disponível localmente ou via Compose | Persistência do backend |
| Docker Compose | opcional | Frontend, backend e PostgreSQL em contêineres |

> Use a versão **final** do Python 3.14: pré-lançamentos (`rc`) podem quebrar a importação do FastAPI/Pydantic.

## 1. Backend

```bash
cd backend
cp ../.env.example .env  # ajuste as credenciais do PostgreSQL se necessário
uv sync                  # cria o ambiente virtual e instala as dependências
uv run alembic upgrade head
uv run uvicorn src.presentation.api.main:app --reload --env-file .env
```

- API: <http://localhost:8000>
- Swagger (documentação interativa): <http://localhost:8000/docs>
- Health check: `GET /` → `{"status": "online", ...}`

## 2. Frontend

```bash
cd frontend
cp .env.example .env     # VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

- App: <http://localhost:5173>

O backend libera CORS apenas para `http://localhost:5173` e `http://127.0.0.1:5173`. Para outra origem, ajuste `allow_origins` em `backend/src/presentation/api/main.py`.

## 3. Usando o app

1. Abra <http://localhost:5173/cadastro> e crie uma conta (senha com no mínimo 6 caracteres).
2. Em **Cadastrar obra**, informe um ISBN com 10+ caracteres, ao menos um autor e a editora.
3. Veja a obra na **Estante**, busque por título/autor e filtre por Mangás ou Quadrinhos.
4. Em **Minhas listas**, crie uma lista e adicione obras a ela.

> A API usa PostgreSQL para persistir usuários, obras, listas e demais dados. Execute as migrations antes da primeira inicialização.

## Testes e qualidade

```bash
# Backend
cd backend
uv run pytest            # unitários (domínio, casos de uso, mappers) e de API
uv run ruff check .      # lint

# Frontend
cd frontend
npm test                 # Vitest (unitários e de integração)
npm run test:coverage    # com relatório de cobertura
npm run test:watch       # modo observação
npm run lint             # oxlint
npm run format:check     # verifica a formatação (Prettier)
npm run format           # formata o código
npm run build            # checagem de tipos (tsc) + build de produção
```

Os testes que exercitam repositórios SQLAlchemy precisam de PostgreSQL acessível com as credenciais configuradas no `backend/.env`; eles criam e removem schemas temporários isolados.

## Variáveis de ambiente

### Backend (`backend/.env`)

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `DB_HOST` / `DB_PORT` | `localhost` / `5432` | Endereço do PostgreSQL |
| `DB_USER` / `DB_PASSWORD` / `DB_NAME` | `postgres` / `postgres` / `mydb` | Credenciais padrão da aplicação; o `.env.example` do projeto define valores próprios |
| `SEED_CATALOG` | `true` | Carrega as 39 obras nativas ao iniciar a API |
| `GOOGLE_BOOKS_API_KEY` | vazio | Opcional. Com a chave, a busca externa usa o Google Books antes do Open Library |
| `CATALOG_TIMEOUT_SECONDS` | `8` | Tempo limite de cada consulta ao catálogo externo |
| `SECRET_KEY` | `your-secret-key` | Segredo de assinatura do JWT. **Troque em produção** e use um valor aleatório forte |
| `ALGORITHM` | `HS256` | Algoritmo do JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Validade do token |
| `API_PORT` | `8000` | Porta publicada para a API pelo Compose |
| `POSTGRES_PORT` | `5432` | Porta publicada para o PostgreSQL pelo Compose |
| `FRONTEND_PORT` | `3000` | Porta publicada para o frontend pelo Compose |

### Frontend (`frontend/.env`)

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `VITE_API_URL` | `http://localhost:8000` | URL base da API |

## Docker

O arquivo `compose.yml`, na raiz do repositório, sobe frontend, API e PostgreSQL:

```bash
cp .env.example .env
docker compose build
docker compose run --rm backend alembic upgrade head
docker compose up
```

O Compose carrega o `.env` da raiz, configura o serviço da API para acessar o banco pelo hostname `postgres` e espera o banco ficar saudável antes de iniciar a API. Por padrão, frontend, API e PostgreSQL ficam disponíveis em `http://localhost:3000`, `http://localhost:8000` e `localhost:5432`. O hostname `postgres` só é resolvido entre containers. Se executar a API com `docker compose run`, use `--service-ports` para publicar a porta.

Para iniciar a API localmente com Uvicorn em vez de executá-la no Docker, configure `DB_HOST=localhost` no `.env` e execute:

```bash
cd backend
uv run alembic upgrade head
uv run uvicorn src.presentation.api.main:app --reload --env-file .env
```

Variáveis do `.env` não alteram automaticamente um volume PostgreSQL já inicializado.

## Notas operacionais

- Os endpoints de produção usam repositórios SQLAlchemy; os adaptadores em memória são reservados aos testes.
- `SEED_CATALOG=true` (padrão) insere no PostgreSQL as obras nativas ainda ausentes ao iniciar a API.
- O Docker Compose e o `.env.example` usados pelo projeto ficam na raiz do repositório.
