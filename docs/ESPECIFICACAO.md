# Especificação do Sistema

Documento técnico com requisitos funcionais, não funcionais, regras de negócio e contrato da API do **Estante**.

## Sumário

- [Visão geral](#visão-geral)
- [Requisitos funcionais](#requisitos-funcionais)
- [Requisitos não funcionais](#requisitos-não-funcionais)
- [Regras de negócio](#regras-de-negócio)
- [Rotas da API](#rotas-da-api)
- [Tratamento de erros](#tratamento-de-erros)

## Visão geral

O Estante permite que pessoas leitoras cadastrem **livros, mangás e quadrinhos**, busquem na estante e organizem suas leituras em **listas**. Mangá e Quadrinhos são tratados como gêneros especiais (campo `genre`); uma obra sem nenhum dos dois é exibida como *Livro*.

## Requisitos funcionais

| ID | Requisito | Tela | Status |
| --- | --- | --- | --- |
| RF01 | O sistema deve permitir criar uma conta com nome de usuário, e-mail e senha | Cadastro | ✓ |
| RF02 | O sistema deve autenticar por e-mail e senha e emitir um token JWT | Login | ✓ |
| RF03 | O sistema deve manter a sessão entre recarregamentos e permitir sair | Navbar | ✓ |
| RF04 | O sistema deve restringir cadastro de obras e listas a usuários autenticados | — | ✓ |
| RF05 | O usuário autenticado deve cadastrar uma obra (título, autores, ISBN, editora, gêneros, temas, tipo) | Cadastrar obra | ✓ |
| RF06 | O sistema deve listar as obras cadastradas em uma grade | Estante | ✓ |
| RF07 | O sistema deve buscar obras por título ou autor | Estante | ✓ |
| RF08 | O sistema deve filtrar obras por Mangás e Quadrinhos | Estante | ✓ |
| RF09 | O sistema deve exibir os detalhes de uma obra | Detalhe da obra | ✓ |
| RF10 | O usuário deve criar, editar e excluir listas de leitura, públicas ou privadas | Minhas listas | ✓ |
| RF11 | O usuário deve visualizar todas as suas listas | Minhas listas | ✓ |
| RF12 | O dono da lista deve adicionar obras a ela | Detalhe da lista | ✓ |
| RF13 | O usuário deve avaliar obras com nota de 1 a 5 e ver a média da obra | Detalhe da obra | ✓ |
| RF14 | O usuário deve escrever e editar uma resenha, podendo marcá-la como spoiler | Detalhe da obra | ✓ |
| RF15 | O usuário deve denunciar conteúdos (Report) | — | ✓ (API) |
| RF16 | O sistema deve listar as resenhas de uma obra, com o texto de spoiler borrado até o leitor pedir para mostrar | Detalhe da obra | ✓ |
| RF17 | O usuário deve curtir e descurtir resenhas (Vote) | Detalhe da obra | ✓ |
| RF18 | A busca da estante deve consultar o catálogo externo e cadastrar obras ao serem abertas | Estante | ✓ |
| RF19 | O usuário deve marcar uma obra como Quero ler, Lendo ou Lido (Reading) | Detalhe da obra | ✓ |
| RF20 | O usuário deve personalizar o perfil com bio, avatar e capa | Editar perfil | ✓ |
| RF21 | O usuário deve comentar nas resenhas de outras pessoas e apagar os próprios comentários | Detalhe da obra | ✓ |
| RF22 | O usuário deve seguir e deixar de seguir outros usuários | Perfil público | ✓ |
| RF23 | O usuário deve seguir e deixar de seguir listas públicas de outras pessoas | Detalhe da lista | ✓ |
| RF24 | O sistema deve exibir o perfil público de um usuário (bio, avatar, capa, seguidores e listas públicas) | Perfil público | ✓ |
| RF25 | O usuário deve ver um feed com as resenhas de quem segue | Feed | ✓ |
| RF26 | O usuário deve receber notificações de curtidas, comentários e novos seguidores | Notificações | ✓ |
| RF27 | O usuário deve escolher quais tipos de notificação receber | Notificações | ✓ |
| RF28 | O sistema deve recomendar obras com base nas avaliações e leituras do usuário | Recomendações | ✓ |

## Requisitos não funcionais

| ID | Categoria | Requisito |
| --- | --- | --- |
| RNF01 | Usabilidade | Interface minimalista, em português, com paleta creme e azul quente e foco visível para navegação por teclado |
| RNF02 | Responsividade | Layout adaptável de celulares a desktops (grade de 2 a 5 colunas) |
| RNF03 | Segurança | Senhas armazenadas com hash **bcrypt**; autenticação por **JWT** com expiração configurável |
| RNF04 | Segurança | A API nunca devolve a senha; credenciais inválidas retornam mensagem única (não revela se o e-mail existe) |
| RNF05 | Segurança | CORS restrito às origens do frontend; listas privadas não vazam a própria existência (404) |
| RNF06 | Arquitetura | Backend em camadas (Clean Architecture/DDD), com regras de negócio independentes de framework |
| RNF07 | Manutenibilidade | Persistência desacoplada por interfaces de repositório |
| RNF08 | Testabilidade | Backend coberto por `pytest` e `pytest-asyncio`; frontend coberto por testes unitários e de integração com Vitest, Testing Library e MSW (veja [Estratégia de testes](TESTES.md)) |
| RNF09 | Portabilidade | Execução do backend e do banco via Docker Compose |
| RNF10 | Desempenho | Busca da estante com *debounce* de 250 ms e cancelamento de requisições obsoletas |
| RNF11 | Qualidade | Lint com `ruff` (backend) e `oxlint` (frontend); formatação do frontend padronizada com Prettier; TypeScript em modo estrito |
| RNF12 | Acessibilidade | Interface em conformidade com a **WCAG 2.1 nível AA**, verificada por testes automáticos (veja [Acessibilidade](ACESSIBILIDADE.md)) |

## Regras de negócio

- **Usuário:** nome com no mínimo 3 caracteres, e-mail válido (contém `@`), senha com no mínimo 6 caracteres, e-mail único (comparado em minúsculas).
- **Obra:** ISBN com no mínimo 10 caracteres e **único**; título, editora e ao menos um autor obrigatórios; gêneros vazios são descartados.
- **Lista:** nome com no mínimo 3 caracteres e **único globalmente**; descrição obrigatória; pertence a quem a criou. Só o dono pode editar ou excluir.
- **Itens da lista:** só o dono adiciona obras; a obra precisa existir e não pode repetir na mesma lista.
- **Lista privada:** só o dono consegue abrir; para os demais, responde como se não existisse.
- **Resenha:** nota de 1 a 5 obrigatória, texto opcional (até 1000 caracteres) e marca de spoiler. O autor vem do token, nunca do corpo. Cada usuário tem **uma** resenha por obra e só o autor a altera.
- **Curtida:** é um voto com `status: "like"` e alvo `reviews`; um voto por usuário e alvo.
- **Status de leitura:** `want_to_read`, `reading` ou `read`; um por usuário e obra, privado a quem marcou. Marcar de novo o mesmo status desmarca no frontend.
- **Comentário:** de 1 a 500 caracteres, em resenhas existentes; só o autor apaga.
- **Seguir:** não é possível seguir a si mesmo; seguir duas vezes não duplica; só listas públicas (ou do próprio usuário) podem ser seguidas.
- **Notificação:** gerada quando outra pessoa curte ou comenta uma resenha sua ou passa a seguir você; nunca para ações do próprio usuário; respeita as preferências de quem recebe.
- **Feed:** resenhas das pessoas seguidas, da mais nova para a mais antiga, até 30 itens.
- **Recomendação:** pontua as obras ainda não vistas pelos gêneros e autores das obras que o usuário avaliou com 4 ou 5 estrelas ou marcou como lendo, lido ou quero ler; autores contam o dobro dos gêneros.
- **Perfil:** bio com até 300 caracteres; avatar e capa são links que precisam começar com `http://` ou `https://` (até 500 caracteres). Campos vazios limpam o valor, e cada pessoa só altera o próprio perfil.
- **Busca externa:** exige login e mínimo de 2 caracteres; consulta o Google Books quando `GOOGLE_BOOKS_API_KEY` está configurada e usa o Open Library como fallback.

## Rotas da API

Documentação interativa (Swagger) em `http://localhost:8000/docs`. [login] = exige `Authorization: Bearer <token>`.

### Autenticação

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Cria a conta e devolve token + usuário | `201` |
| `POST` | `/auth/login` | Autentica e devolve token + usuário | `200` |
| `GET` | `/auth/me` [login] | Usuário da sessão atual, com `bio`, `avatar_url` e `cover_url` | `200` |
| `PUT` | `/auth/me` [login] | Atualiza `bio`, `avatar_url` e `cover_url` do usuário logado | `200` |

### Obras

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/books?q=&genre=` | Lista obras; `q` busca em título **ou** autor, `genre` filtra por gênero | `200` |
| `GET` | `/books/{id}` | Detalhes de uma obra | `200` |
| `POST` | `/books` [login] | Cadastra uma obra | `201` |
| `PUT` | `/books/{id}` [login] | Edita uma obra | `200` |
| `DELETE` | `/books/{id}` [login] | Exclui uma obra | `204` |

### Listas

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/lists` [login] | Listas da pessoa autenticada | `200` |
| `POST` | `/lists` [login] | Cria uma lista | `201` |
| `PUT` | `/lists/{id}` [login] | Edita nome, descrição e privacidade; só o dono | `200` |
| `DELETE` | `/lists/{id}` [login] | Exclui a lista; só o dono | `204` |
| `GET` | `/lists/{id}` [login] | Detalhes de uma lista (com as obras) | `200` |
| `POST` | `/lists/{id}/books` [login] | Adiciona uma obra à lista (`{"book_id": 1}`) | `200` |

### Catálogo externo

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/catalog/search?q=` [login] | Busca no Google Books (se configurado), com fallback para Open Library; devolve `isbn`, `title`, `authors`, `publisher`, `genres` e `cover_url` | `200` |

### Resenhas

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/reviews` | Lista resenhas; filtros `book_id`, `user_id`, `rating`, `username`, `book_title`, `comment`. Cada item traz `username`, `likes`, `liked_by_me` e `like_vote_id` (este com login opcional) | `200` |
| `GET` | `/reviews/{id}` | Detalhes de uma resenha | `200` |
| `GET` | `/reviews/feed?page=&sort=` | Feed paginado; `sort` aceita `recent` ou `popular` | `200` |
| `POST` | `/reviews` [login] | Cria a resenha (`rating`, `comment`, `isSpoiler`, `book_id`); o autor é o usuário logado | `201` |
| `PUT` | `/reviews/{id}` [login] | Edita nota, texto e spoiler; só o autor | `200` |
| `PATCH` | `/reviews/{id}/spoiler` [login] | Liga ou desliga a marca de spoiler; só o autor | `200` |

### Votos

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `POST` | `/votes` [login] | Registra um voto (`status`, `target_entity`: `lists`, `books` ou `reviews`, `target_id`) | `201` |
| `GET` | `/votes` [login] | Lista votos com filtros `status`, `user_name`, `target_type` e `target_name` | `200` |
| `GET` | `/votes/{id}` [login] | Detalhes do voto | `200` |
| `DELETE` | `/votes/{id}` [login] | Remove o voto | `204` |
| `GET` | `/votes/favorites` [login] | Lista os livros favoritos do usuário | `200` |
| `PUT` | `/votes/favorites/{book_id}` [login] | Adiciona o livro aos favoritos; operação idempotente | `204` |
| `DELETE` | `/votes/favorites/{book_id}` [login] | Remove o livro dos favoritos | `204` |

### Status de leitura

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/readings?book_id=&status=` [login] | Status de leitura do usuário logado | `200` |
| `PUT` | `/readings/{book_id}` [login] | Define o status (`{"status": "reading"}`); cria ou atualiza | `200` |
| `DELETE` | `/readings/{book_id}` [login] | Remove a marcação | `204` |

### Comentários

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/reviews/{id}/comments` | Lista os comentários de uma resenha | `200` |
| `POST` | `/reviews/{id}/comments` [login] | Comenta (`{"text": "..."}`) e notifica o autor da resenha | `201` |
| `DELETE` | `/comments/{id}` [login] | Apaga o próprio comentário | `204` |

### Seguidores e perfil público

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/users/{id}` | Perfil público com `followers`, `following` e `is_following` (login opcional) | `200` |
| `GET` | `/users/{id}/lists` | Listas públicas do usuário | `200` |
| `GET` | `/follows?type=` [login] | O que o usuário logado segue (`users` ou `lists`) | `200` |
| `GET` | `/follows/{users\|lists}/{id}` | Se o usuário segue e o total de seguidores | `200` |
| `PUT` | `/follows/{users\|lists}/{id}` [login] | Segue o alvo; seguir um usuário gera notificação | `200` |
| `DELETE` | `/follows/{users\|lists}/{id}` [login] | Deixa de seguir | `200` |

### Notificações

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/notifications` [login] | Lista as últimas 50 e o total de não lidas | `200` |
| `POST` | `/notifications/read` [login] | Marca todas como lidas | `204` |
| `PATCH` | `/notifications/{id}/read` [login] | Marca uma como lida | `204` |
| `GET` | `/notifications/preferences` [login] | Preferências (`likes`, `comments`, `follows`) | `200` |
| `PUT` | `/notifications/preferences` [login] | Atualiza as preferências | `200` |

### Feed e recomendações

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/feed` [login] | Resenhas de quem o usuário segue, com `book_title` | `200` |
| `GET` | `/recommendations` [login] | Até 10 obras com o motivo da sugestão | `200` |

### Denúncias

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `POST` | `/reports` [login] | Cria denúncia; `user_id` é obtido da sessão autenticada | `201` |
| `GET` | `/reports/{report_id}` [login] | Busca denúncia por ID | `200` |
| `GET` | `/reports` [login] | Lista denúncias; aceita filtros `user_id`, `target_id` e `target_entity` | `200` |

## Tratamento de erros

Os erros seguem o formato `{"detail": ...}`. Erros de validação do Pydantic podem trazer uma lista em `detail`; o cliente do frontend trata tanto mensagens de texto quanto essa lista.

| Código | Quando |
| --- | --- |
| `401` | Sem token, token inválido/expirado ou credenciais erradas |
| `403` | Alterar lista ou resenha de outra pessoa, ou apagar comentário de outra pessoa |
| `404` | Obra ou lista inexistente (ou lista privada de terceiros) |
| `409` | E-mail, username, ISBN ou nome de lista já cadastrados; obra repetida na lista; segunda resenha da mesma obra; voto ou denúncia duplicados |
| `422` | Dados inválidos (validação do Pydantic ou regras do domínio) |
| `502` | Catálogo externo indisponível |
