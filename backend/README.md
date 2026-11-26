# Servidor do projeto books

API provedora de serviços para a aplicação, desenvolvida em FastAPI seguindo os critérios fornecidos pelo professor Juan Hassan da disciplina Laboratório de Engenharia de Software pela Fatec de São José dos Campos.

## Sumário
- [Como Executar](#how_to_run)
- [Arquitetura da Aplicação](#app_architecture)
- [Diagrama de Entidade e Relacionamento](#der)
- [Rotas da Aplicação](#app_route)
- [Tecnologias Utilizadas](#technology)

## <span id="how_to_run"> Como Executar </span>

```bash
cd backend
cp ../.env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn src.presentation.api.main:app --reload --env-file .env
```

- API em <http://localhost:8000> e Swagger em <http://localhost:8000/docs>
- O arquivo `.env.example` fica na raiz do repositório; ajuste as credenciais do PostgreSQL antes de executar as migrations.
- Testes (com PostgreSQL disponível): `uv run pytest` · Lint: `uv run ruff check .`
- Guia completo (Docker, migrations, variáveis): [Manual de Execução](../docs/MANUAL_EXECUCAO.md)

## <span id="app_architecture"> Arquitetura da aplicação </span>

Organizada em camadas com Clean Architecture / DDD: os casos de uso dependem das interfaces do domínio, e os providers da API injetam os repositórios SQLAlchemy.

| Diretório | Função |
| --- | --- |
| `src/domain` | Entidades (`Book`, `BookList`, `User`), exceções de domínio e interfaces de repositório |
| `src/application/use_cases` | Um caso de uso por ação (`CreateBook`, `SearchBooks`, `AuthenticateUser`, `AddBookToList`…) |
| `src/infrastructure` | Repositórios SQLAlchemy, adaptadores em memória usados nos testes, mappers, hash de senha (bcrypt) e JWT |
| `src/presentation/api` | Routers FastAPI, schemas Pydantic e dependências (usuário autenticado) |
| `src/core` | Configurações lidas das variáveis de ambiente |
| `tests` | Testes unitários, de integração com a API e de persistência (`pytest`) |

Design patterns aplicados: **Repository**, **Data Mapper** e **Dependency Injection** — detalhes em [Arquitetura](../docs/ARQUITETURA.md#design-patterns).

## <span id="der"> Diagrama de Entidade e Relacionamento (DER) </span>
O DER textual atualizado está em [Modelagem de Dados](../docs/MODELAGEM_DADOS.md).

### Entidades
- User (Usuário do sistema)
  - ID (Identificador único) - Gerado automaticamente
  - Username (Nome de usuário) - Obrigatório
  - Email (Email) - Obrigatório
  - Password (Senha) - Obrigatório
  - Role (Papel; padrão `user`)
  - Created_at (Data de criação) - Gerado automaticamente
  - Bio (Texto de apresentação, até 300 caracteres) - Opcional
  - Avatar_url (Link da foto do perfil) - Opcional
  - Cover_url (Link da capa do perfil) - Opcional
- Book (Livros)
  - ID (Identificador único) - Gerado automaticamente
  - ISBN (ISBN do livro) - Obrigatório e único
  - Genre (Gênero) - Multivalorado obrigatório
  - Theme (Tema) - Multivalorado opcional (padrão vazio)
  - Title (Título) - Obrigatório
  - Author (Autor) - Multivalorado obrigatório
  - Publisher (Editora) - Obrigatório
- List (Uma lista de livros criada pelo usuário)
  - ID (Identificador único) - Gerado automaticamente
  - Owner (ID do usuário proprietário)
  - Name (Nome) - Obrigatório e único globalmente
  - Description (Descrição breve) - Obrigatória
  - `private` (Indica se a lista é privada; padrão falso)
- Review (Review de algum livro)
  - ID (Identificador único) - Gerado automaticamente
  - User_ID (ID do Usuário) - Obtido da sessão autenticada
  - Book_ID (ID do Livro) - O front passa automaticamente
  - Comment (Comentário) - Opcional
  - Rating (Avaliação em estrelas) - Obrigatório (vai de 1 a 5)
  - isSpoiler (Indica que o texto revela partes da obra) - Opcional (padrão falso)
- Vote (O usuário pode registrar um único like/dislike ou marcação por alvo, alvos diferentes aceitam votos independentes)
  - ID (Identificador único) - Gerado automaticamente
  - User_ID (ID do Usuário) - Obtido da sessão autenticada
  - Target_ID (ID do Alvo) - O front passa automaticamente
  - Target_Entity (Entidade do alvo) - O front passa automaticamente
  - Status (Indica o conteúdo do voto) - Obrigatório
- Comment (Comentário em uma resenha: texto de até 500 caracteres, autor e resenha)
- Follow (Seguidor, alvo `users` ou `lists` e id do alvo; único por seguidor e alvo)
- Notification (Aviso de curtida, comentário ou novo seguidor, com `read`) e NotificationPreference (o que o usuário quer receber)
- Reading (Status de leitura de uma obra por usuário)
  - ID (Identificador único) - Gerado automaticamente
  - User_ID (ID do Usuário) - Obtido da sessão autenticada
  - Book_ID (ID do Livro) - Obrigatório
  - Status (`want_to_read`, `reading` ou `read`) - Obrigatório
- Report (Usuários autenticados podem denunciar conteúdos por meio de `/reports`; `target_entity` é texto)
  - ID (Identificador único) - Gerado automaticamente
  - User_ID (ID do Usuário) - Obtido da sessão autenticada
  - Target_ID (ID do Alvo) - O front passa automaticamente
  - Target_Entity (Entidade do alvo) - O front passa automaticamente
  - Description (Descrição do motivo da denúncia) - Obrigatório

## <span id="app_route"> Rotas da Aplicação </span>

[login] = exige `Authorization: Bearer <token>`. Detalhes e códigos de erro na [Especificação](../docs/ESPECIFICACAO.md#rotas-da-api).

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/` | Health check |
| `POST` | `/auth/register` | Cria conta e devolve token |
| `POST` | `/auth/login` | Autentica e devolve token |
| `POST` | `/reports` [login] | Cria denúncia persistida no PostgreSQL; o autor vem da sessão |
| `GET` | `/reports/{report_id}` [login] | Busca denúncia por ID |
| `GET` | `/reports` [login] | Lista denúncias com filtros opcionais |
| `GET` | `/auth/me` [login] | Usuário da sessão |
| `PUT` | `/auth/me` [login] | Atualiza bio, avatar e capa do perfil |
| `GET` | `/books?q=&genre=` | Lista/busca obras |
| `GET` | `/books/{id}` | Detalhes da obra |
| `POST` | `/books` [login] | Cadastra obra |
| `PUT` | `/books/{id}` [login] | Edita obra |
| `DELETE` | `/books/{id}` [login] | Exclui obra |
| `GET` | `/catalog/search?q=` [login] | Busca no Google Books (se configurado), com fallback para Open Library |
| `GET` | `/reviews?book_id=&user_id=` | Lista resenhas (com `username`, `likes`, `liked_by_me`) |
| `GET` | `/reviews/feed?page=&sort=` | Feed paginado de resenhas (`recent` ou `popular`) |
| `GET` | `/reviews/{id}` | Detalhes da resenha |
| `POST` | `/reviews` [login] | Cria a resenha do usuário logado; uma por obra (`409` se repetir) |
| `PUT` | `/reviews/{id}` [login] | Edita nota, texto e spoiler; só o autor (`403` para outros) |
| `PATCH` | `/reviews/{id}/spoiler` [login] | Liga ou desliga o spoiler; só o autor |
| `GET` | `/reviews/{id}/comments` | Lista os comentários da resenha |
| `POST` | `/reviews/{id}/comments` [login] | Comenta e notifica o autor |
| `DELETE` | `/comments/{id}` [login] | Apaga o próprio comentário |
| `GET` | `/users/{id}` | Perfil público com seguidores |
| `GET` | `/users/{id}/lists` | Listas públicas do usuário |
| `PUT` / `DELETE` | `/follows/{users\|lists}/{id}` [login] | Segue ou deixa de seguir |
| `GET` | `/follows/{users\|lists}/{id}` | Estado e total de seguidores (login opcional) |
| `GET` | `/follows?type=` [login] | Lista usuários ou listas seguidos |
| `GET` | `/notifications` [login] | Notificações e total de não lidas |
| `POST` | `/notifications/read` [login] | Marca todas as notificações como lidas |
| `PATCH` | `/notifications/{id}/read` [login] | Marca uma notificação como lida |
| `GET` / `PUT` | `/notifications/preferences` [login] | Preferências de notificação |
| `GET` | `/feed` [login] | Resenhas de quem o usuário segue |
| `GET` | `/recommendations` [login] | Obras recomendadas |
| `GET` | `/readings?book_id=&status=` [login] | Status de leitura do usuário logado |
| `PUT` | `/readings/{book_id}` [login] | Define Quero ler, Lendo ou Lido |
| `DELETE` | `/readings/{book_id}` [login] | Remove a marcação |
| `GET` | `/lists` [login] | Minhas listas |
| `POST` | `/lists` [login] | Cria lista |
| `PUT` | `/lists/{id}` [login] | Edita nome, descrição e privacidade da lista |
| `DELETE` | `/lists/{id}` [login] | Exclui a lista |
| `GET` | `/lists/{id}` [login] | Detalhes da lista |
| `POST` | `/lists/{id}/books` [login] | Adiciona obra à lista |
| `POST` | `/votes` [login] | Registra um voto por usuário e alvo; uma tentativa duplicada retorna `409` |
| `GET` | `/votes?status=&user_name=&target_type=&target_name=` [login] | Lista votos por status, username e alvo (título do livro, nome da lista ou comentário da review) |
| `GET` | `/votes/favorites` [login] | Lista os livros favoritos do usuário |
| `PUT` / `DELETE` | `/votes/favorites/{book_id}` [login] | Adiciona ou remove um livro dos favoritos |
| `GET` | `/votes/{id}` [login] | Detalhes do voto |
| `DELETE` | `/votes/{id}` [login] | Exclui voto |

## <span id="technology"> Tecnologias Utilizadas </span>
- Backend
![Python](https://img.shields.io/badge/python-%233670A0.svg?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/fastapi-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/sqlalchemy-%23D71F00.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-1f6feb?style=for-the-badge)
![JWT](https://img.shields.io/badge/json%20web%20tokens-%23000000.svg?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

- Database
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

- Tests
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)

- DevOps
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)