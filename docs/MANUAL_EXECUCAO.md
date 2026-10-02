# Manual de Execução

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [1. Backend](#1-backend)
- [2. Frontend](#2-frontend)
- [3. Usando o app](#3-usando-o-app)
- [Testes e qualidade](#testes-e-qualidade)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Docker](#docker)
- [Pendências conhecidas](#pendencias-conhecidas)

## Pré-requisitos

| Ferramenta | Versão | Uso |
| --- | --- | --- |
| Python | 3.14 (versão final) | Backend |
| [uv](https://docs.astral.sh/uv/) | recente | Gerenciador de dependências do backend |
| Node.js | 22 ou superior | Frontend |
| Docker | opcional | PostgreSQL e backend em contêiner |

> Use a versão **final** do Python 3.14: pré-lançamentos (`rc`) podem quebrar a importação do FastAPI/Pydantic.

## 1. Backend

```bash
cd backend
cp .env.example .env     # ajuste os valores se necessário
uv sync                  # cria o ambiente virtual e instala as dependências
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

> Os dados da API ficam **em memória** e são perdidos ao reiniciar o servidor (veja [Pendências](#pendencias-conhecidas)).

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

## Variáveis de ambiente

### Backend (`backend/.env`)

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `DATABASE_URL` | — | URL do PostgreSQL (`postgresql+asyncpg://usuario:senha@host:5432/banco`) |
| `SECRET_KEY` | chave de desenvolvimento | Segredo de assinatura do JWT. **Troque em produção** (32+ caracteres) |
| `ALGORITHM` | `HS256` | Algoritmo do JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Validade do token |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | — | Credenciais do contêiner PostgreSQL |
| `API_PORT` | `8000` | Porta publicada pelo Docker Compose |

### Frontend (`frontend/.env`)

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `VITE_API_URL` | `http://localhost:8000` | URL base da API |

## Docker

O `backend/docker-compose.yml` sobe a API e o PostgreSQL:

```bash
cd backend
docker compose up --build
```

Migrations do banco (Alembic):

```bash
cd backend
uv run alembic upgrade head
```

<a id="pendencias-conhecidas"></a>

## Pendências conhecidas

Pontos identificados ao documentar que o time deve resolver antes da entrega final:

| Item | Situação | O que fazer |
| --- | --- | --- |
| **SQLite no código** | `src/infrastructure/persistence/database.py` e `alembic.ini` ainda apontam para SQLite, **proibido** pelos critérios | Usar `settings.DATABASE_URL` (PostgreSQL) nos dois |
| **Persistência da API** | Usuários, obras e listas usam repositórios em memória; só `books` tem repositório SQLAlchemy | Criar modelos/migrations de `users` e `lists` e trocar os `Depends` |
| **Dockerfile** | `CMD` aponta para `src.main:app` | Trocar por `src.presentation.api.main:app` |
| **Review, Vote e Report** | Previstas no DER, sem implementação | Ver RF13 a RF15 na [especificação](ESPECIFICACAO.md#requisitos-funcionais) |
| **Nome de lista único global** | Duas pessoas não podem ter listas com o mesmo nome | Tornar a unicidade por dono |
