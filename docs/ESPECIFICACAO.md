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
| RF01 | O sistema deve permitir criar uma conta com nome de usuário, e-mail e senha | Cadastro | ✅ |
| RF02 | O sistema deve autenticar por e-mail e senha e emitir um token JWT | Login | ✅ |
| RF03 | O sistema deve manter a sessão entre recarregamentos e permitir sair | Navbar | ✅ |
| RF04 | O sistema deve restringir cadastro de obras e listas a usuários autenticados | — | ✅ |
| RF05 | O usuário autenticado deve cadastrar uma obra (título, autores, ISBN, editora, gêneros, temas, tipo) | Cadastrar obra | ✅ |
| RF06 | O sistema deve listar as obras cadastradas em uma grade | Estante | ✅ |
| RF07 | O sistema deve buscar obras por título ou autor | Estante | ✅ |
| RF08 | O sistema deve filtrar obras por Mangás e Quadrinhos | Estante | ✅ |
| RF09 | O sistema deve exibir os detalhes de uma obra | Detalhe da obra | ✅ |
| RF10 | O usuário deve criar listas de leitura, públicas ou privadas | Minhas listas | ✅ |
| RF11 | O usuário deve visualizar todas as suas listas | Minhas listas | ✅ |
| RF12 | O dono da lista deve adicionar obras a ela | Detalhe da lista | ✅ |
| RF13 | O usuário deve avaliar obras com nota de 1 a 5 e comentário (Review) | — | 🔜 previsto no DER |
| RF14 | O usuário deve votar (like/dislike/marcações) em conteúdos (Vote) | — | 🔜 previsto no DER |
| RF15 | O usuário deve denunciar conteúdos (Report) | — | 🔜 previsto no DER |

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

## Regras de negócio

- **Usuário:** nome com no mínimo 3 caracteres, e-mail válido (contém `@`), senha com no mínimo 6 caracteres, e-mail único (comparado em minúsculas).
- **Obra:** ISBN com no mínimo 10 caracteres e **único**; título, editora e ao menos um autor obrigatórios; gêneros vazios são descartados.
- **Lista:** nome com no mínimo 3 caracteres e **único**; descrição obrigatória; pertence a quem a criou.
- **Itens da lista:** só o dono adiciona obras; a obra precisa existir e não pode repetir na mesma lista.
- **Lista privada:** só o dono consegue abrir; para os demais, responde como se não existisse.

## Rotas da API

Documentação interativa (Swagger) em `http://localhost:8000/docs`. 🔒 = exige `Authorization: Bearer <token>`.

### Autenticação

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Cria a conta e devolve token + usuário | `201` |
| `POST` | `/auth/login` | Autentica e devolve token + usuário | `200` |
| `GET` | `/auth/me` 🔒 | Usuário da sessão atual | `200` |

### Obras

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/books?q=&genre=` | Lista obras; `q` busca em título **ou** autor, `genre` filtra por gênero | `200` |
| `GET` | `/books/{id}` | Detalhes de uma obra | `200` |
| `POST` | `/books` 🔒 | Cadastra uma obra | `201` |

### Listas

| Método | Rota | Descrição | Sucesso |
| --- | --- | --- | --- |
| `GET` | `/lists` 🔒 | Listas da pessoa autenticada | `200` |
| `POST` | `/lists` 🔒 | Cria uma lista | `201` |
| `GET` | `/lists/{id}` 🔒 | Detalhes de uma lista (com as obras) | `200` |
| `POST` | `/lists/{id}/books` 🔒 | Adiciona uma obra à lista (`{"book_id": 1}`) | `200` |

## Tratamento de erros

Todos os erros seguem o formato `{"detail": "mensagem"}`; o frontend exibe a mensagem diretamente.

| Código | Quando |
| --- | --- |
| `401` | Sem token, token inválido/expirado ou credenciais erradas |
| `403` | Alterar lista de outra pessoa |
| `404` | Obra ou lista inexistente (ou lista privada de terceiros) |
| `409` | E-mail, ISBN ou nome de lista já cadastrados; obra repetida na lista |
| `422` | Dados inválidos (validação do Pydantic ou regras do domínio) |
