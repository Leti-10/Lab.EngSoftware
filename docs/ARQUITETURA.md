# Arquitetura

## Sumário

- [Visão de integração](#visão-de-integração-react--python--banco)
- [Camadas do backend](#camadas-do-backend)
- [Design Patterns](#design-patterns)
- [Frontend](#frontend)
- [Fluxo de uma requisição](#fluxo-de-uma-requisição)

## Visão de integração (React + Python + Banco)

```mermaid
flowchart TB
    subgraph Navegador
        direction TB
        UI["React 19 + TypeScript<br/>Pages · Components"]
        AUTH["AuthContext<br/>(token JWT no localStorage)"]
        CLIENT["lib/api.ts<br/>fetch + Bearer token"]
        UI --> AUTH --> CLIENT
        UI --> CLIENT
    end

    subgraph "Backend · FastAPI :8000"
        direction TB
        ROUTES["Presentation<br/>routers + schemas Pydantic"]
        USECASES["Application<br/>casos de uso"]
        DOMAIN["Domain<br/>entidades + interfaces de repositório"]
        INFRA["Infrastructure<br/>repositórios · mappers · segurança"]
        ROUTES --> USECASES --> DOMAIN
        INFRA -. implementa .-> DOMAIN
        USECASES --> INFRA
    end

    DB[("PostgreSQL :5432<br/>Alembic migrations")]

    CLIENT -- "HTTP REST · JSON<br/>CORS liberado para :5173" --> ROUTES
    INFRA -- "SQLAlchemy async + asyncpg" --> DB
```

| Parte | Tecnologia | Porta |
| --- | --- | --- |
| Frontend | React 19, TypeScript, Vite, Tailwind 4, React Router | `5173` |
| Backend | Python 3.14, FastAPI, Pydantic, PyJWT, bcrypt | `8000` |
| Banco | PostgreSQL, SQLAlchemy 2 (async), Alembic | `5432` |

## Camadas do backend

A regra de dependência aponta sempre **para o núcleo**: `presentation → application → domain`, com `infrastructure` implementando as interfaces do `domain`.

```text
backend/src/
├── alembic
│   └── versions                # Migrations da evolução do banco de dados
├── src
│   ├── application             # Casos de uso de cada entidade (CreateBook, SearchBooks, AuthenticateUser, ...)
│   │   └── use_cases
│   │       ├── book
│   │       ├── book_list
│   │       ├── review
│   │       └── user
│   ├── core                    # Configurações centralizadas para toda aplicação
│   ├── domain                  # Núcleo da aplicação
│   │   ├── entities            # Entidades puras mapeadas com dataclass
│   │   ├── exceptions          # Exceptions personalizadas para os casos de uso
│   │   └── repositories        # Implementação do respository pattern como classes abstratas
│   ├── infrastructure          # Implementações concretas
│   │   ├── persistence         # Elementos de persistência
│   │   │   ├── mappers         # Mapeamento de entidades puras para implementações concretas
│   │   │   ├── models          # Modelos do SQLAlchemy pra implementação concreta das entidades
│   │   │   └── repositories    # Implementação concreta dos repositories com SQLAlchemy
│   │   ├── security            # Configurações de segurança como criptografia e jwt
│   │   └── seed                # Alimentação inicial dos dados para testes
│   └── presentation            # Camada de apresentação
│       └── api                 # FastAPI
│           ├── routes          # Implementação de rotas
│           └── schemas         # Schemas pydantic para validação de entrada/saída
└── tests
    └── unit                    # Testes unitários usados no TDD
        ├── [...]
```

| Camada | Conhece | Responsabilidade |
| --- | --- | --- |
| `domain` | Nada externo | Regras e invariantes (ex.: ISBN ≥ 10 caracteres) |
| `application` | `domain` | Orquestra uma ação do usuário (ex.: impedir ISBN duplicado) |
| `infrastructure` | `domain` | Implementações concretas: banco, bcrypt, JWT |
| `presentation` | `application`, `domain` | HTTP: valida entrada, chama o caso de uso, traduz erros em status |

## Design Patterns

### 1. Repository

Isola o acesso a dados atrás de uma interface do domínio. Os casos de uso dependem da abstração, nunca do banco.

- Interfaces: [`BookRepository`](../backend/src/domain/repositories/book_repository.py), `UserRepository`, `BookListRepository`
- Implementações: `InMemoryBookRepository` (testes e desenvolvimento) e `SQLAlchemyRepository` (PostgreSQL)

```python
class SearchBooksUseCase:
    def __init__(self, book_repository: BookRepository):  # abstração, não o banco
        self.book_repository = book_repository
```

Benefício: os testes de casos de uso rodam sem banco, e trocar a persistência não altera regra de negócio.

### 2. Data Mapper

[`BookMapper`](../backend/src/infrastructure/persistence/mappers/book_mapper.py) converte entre a **entidade de domínio** (`dataclass`) e o **modelo SQLAlchemy**, mantendo o domínio livre de ORM.

```python
BookMapper.to_sqlalchemy(book)   # domínio → tabela
BookMapper.to_domain(db_model)   # tabela  → domínio
```

### 3. Dependency Injection

O `Depends` do FastAPI injeta repositório e usuário logado nos endpoints, e os testes de API trocam as implementações com `app.dependency_overrides`.

```python
async def create_book(
    payload: CreateBookSchema,
    repository: BookRepository = Depends(get_book_m_repository),
    _current_user: User = Depends(get_current_user),
): ...
```

### Também presentes

- **Use Case (Application Service):** uma classe por ação do usuário, com um único método `execute`.
- **Exceções de domínio:** hierarquia a partir de `DomainError`, traduzida para status HTTP na camada de apresentação.

## Frontend

```text
frontend/src/
├── pages/        # Uma tela por arquivo (Login, Cadastro, Catálogo, Detalhe, Listas…)
├── components/   # Layout, Navbar, BookCard e primitivos de UI (Button, Field, Card, Alert)
├── auth/         # AuthContext (sessão) e ProtectedRoute (rotas que exigem login)
└── lib/          # Cliente HTTP, tipos da API e helpers de obras
```

- **Estado de sessão:** `AuthProvider` guarda o usuário e restaura a sessão chamando `/auth/me` com o token salvo.
- **Rotas protegidas:** `ProtectedRoute` redireciona para `/login` e devolve a pessoa à página original após entrar.
- **Cliente HTTP:** `api()` injeta o `Authorization`, converte erros do FastAPI em mensagens legíveis e suporta cancelamento.

## Fluxo de uma requisição

Exemplo: cadastrar uma obra.

```mermaid
sequenceDiagram
    actor U as Pessoa
    participant P as BookFormPage
    participant A as FastAPI (router)
    participant C as CreateBookUseCase
    participant R as BookRepository

    U->>P: Preenche e envia o formulário
    P->>A: POST /books (Bearer JWT)
    A->>A: get_current_user valida o token
    A->>C: execute(Book)
    C->>R: get_by_isbn(isbn)
    R-->>C: nenhum livro
    C->>R: save(book)
    R-->>C: livro com id
    C-->>A: livro criado
    A-->>P: 201 + BookResponse
    P->>U: Redireciona para /livros/{id}
```
