# Modelagem de Dados

## Diagrama Entidade-Relacionamento (DER)

![DER](../img/der.png)

Versão textual do mesmo modelo, renderizada pelo GitHub:

```mermaid
erDiagram
    USER ||--o{ USER_LIST : cria
    LIST ||--|{ USER_LIST : "é criada por"
    LIST ||--o{ BOOK_LIST : possui
    BOOK ||--o{ BOOK_LIST : "está em"
    USER ||--o{ REVIEW : escreve
    BOOK ||--o{ REVIEW : recebe
    LIST ||--o{ LIST_REVIEW : avalia
    REVIEW ||--o{ LIST_REVIEW : "avalia"
    USER ||--o{ VOTE : vota
    USER ||--o{ READING : marca
    REVIEW ||--o{ COMMENT : recebe
    USER ||--o{ COMMENT : escreve
    USER ||--o{ FOLLOW : segue
    USER ||--o{ NOTIFICATION : recebe
    USER ||--|| NOTIFICATION_PREFERENCE : configura
    BOOK ||--o{ READING : recebe
    USER ||--o{ REPORT : realiza

    USER {
        int id PK
        string name
        string email
        string password
        string role
        datetime created_at
        string bio
        string avatar_url
        string cover_url
    }
    BOOK {
        int id PK
        string isbn
        string title
        string publisher
        string_array author
        string_array genre
        string_array theme
    }
    LIST {
        int id PK
        string name
        string description
        bool is_private
    }
    USER_LIST {
        int user_id FK
        int list_id FK
    }
    BOOK_LIST {
        int list_id FK
        int book_id FK
    }
    REVIEW {
        int id PK
        int user_id FK
        int book_id FK
        string comment
        int rating
        bool isSpoiler
    }
    COMMENT {
        int id PK
        int review_id FK
        int user_id FK
        string text
        datetime created_at
    }
    FOLLOW {
        int id PK
        int follower_id FK
        string target_type
        int target_id
        datetime created_at
    }
    NOTIFICATION {
        int id PK
        int user_id FK
        int actor_id FK
        string type
        int review_id
        int book_id
        bool read
        datetime created_at
    }
    NOTIFICATION_PREFERENCE {
        int user_id PK
        bool likes
        bool comments
        bool follows
    }
    READING {
        int id PK
        int user_id FK
        int book_id FK
        string status
    }
    LIST_REVIEW {
        int list_id FK
        int review_id FK
    }
    VOTE {
        int id PK
        int user_id FK
        int target_id
        string target_entity
        string status
    }
    REPORT {
        int id PK
        int user_id FK
        int target_id
        string target_entity
        string description
    }
```

## Entidades

| Entidade | Descrição | Campos principais |
| --- | --- | --- |
| **User** | Pessoa usuária do sistema | `id`, `name`, `email`, `password` (hash), `role` (comum, desenvolvedor, admin), `created_at`, `bio`, `avatar_url`, `cover_url` (os três opcionais) |
| **Book** | Livro, mangá ou quadrinho | `id`, `isbn`, `title`, `publisher`, `author` (multivalorado), `genre` (multivalorado), `theme` (multivalorado) |
| **List** | Lista de obras criada por um usuário | `id`, `name`, `description`, `is_private` |
| **Review** | Avaliação de uma obra | `id`, `user_id`, `book_id`, `comment` (opcional), `rating` (1 a 5), `isSpoiler` |
| **Vote** | Like/dislike ou marcação em um conteúdo (a curtida de resenha usa `status: "like"` e alvo `reviews`) | `id`, `user_id`, `target_id`, `target_entity`, `status` |
| **Comment** | Comentário em uma resenha | `id`, `review_id`, `user_id`, `text` (até 500), `created_at` |
| **Follow** | Quem segue um usuário ou uma lista | `id`, `follower_id`, `target_type` (`users` ou `lists`), `target_id`, `created_at`; único por seguidor e alvo |
| **Notification** | Aviso de curtida, comentário ou novo seguidor | `id`, `user_id` (quem recebe), `actor_id`, `type`, `review_id`, `book_id`, `read`, `created_at` |
| **NotificationPreference** | Tipos de aviso que o usuário quer receber | `user_id`, `likes`, `comments`, `follows` |
| **Reading** | Status de leitura de uma obra por usuário | `id`, `user_id`, `book_id`, `status` (`want_to_read`, `reading`, `read`); único por usuário e obra |
| **Report** | Denúncia de conteúdo | `id`, `user_id`, `target_id`, `target_entity`, `description` |
| **User_List**, **Book_List**, **List_Review** | Tabelas associativas (N:N) | chaves estrangeiras das entidades relacionadas |

## Como o DER aparece no código

| Entidade | Entidade de domínio | Tabela (Alembic/SQLAlchemy) | Exposta na API |
| --- | --- | --- | --- |
| User | ✓ `domain/entities/user.py` | ✓ `users` | ✓ `/auth/*` |
| Book | ✓ `domain/entities/book.py` | ✓ `books`, `authors`, `book_author` | ✓ `/books` |
| List | ✓ `domain/entities/book_list.py` | Previsto | ✓ `/lists` |
| Review | ✓ `domain/entities/review.py` | ✓ `reviews` | ✓ `/reviews` |
| Vote | ✓ `domain/entities/vote.py` | ✓ `votes` | ✓ `/votes` |
| Comment, Follow, Notification, NotificationPreference | ✓ `domain/entities/social.py` | ✓ `comments`, `follows`, `notifications`, `notification_preferences` | ✓ `/reviews/{id}/comments`, `/follows`, `/notifications` |
| Reading | ✓ `domain/entities/reading.py` | ✓ `readings` | ✓ `/readings` |
| Report | ✓ `domain/entities/report.py` | ✓ `reports` | ✓ `/reports` |

`Report.target_entity` e `Report.target_id` formam uma referência polimórfica. O alvo pode ser um usuário (por exemplo, `target_entity: "users"`) ou outro tipo de conteúdo; por isso, `target_id` não possui uma FK fixa. O autor (`user_id`) é obtido do token da sessão autenticada. Como os usuários são atualmente armazenados em um repositório em memória, `reports.user_id` não possui FK para `users.id`.

> `follows.target_id` é polimórfico (usuário ou lista), sem chave estrangeira. `notifications.review_id` e `notifications.book_id` também não têm.

> `reviews.book_id` e `readings.book_id` não têm chave estrangeira para `books`, porque as obras ainda ficam em memória (veja as [pendências](MANUAL_EXECUCAO.md#pendencias-conhecidas)).

> Na implementação atual, o autor é normalizado em uma tabela própria (`authors`) ligada a `books` por `book_author`; gênero e tema ainda não têm tabela.
