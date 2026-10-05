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
    USER ||--o{ REPORT : realiza

    USER {
        int id PK
        string name
        string email
        string password
        string role
        datetime created_at
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
| **User** | Pessoa usuária do sistema | `id`, `name`, `email`, `password` (hash), `role` (comum, desenvolvedor, admin), `created_at` |
| **Book** | Livro, mangá ou quadrinho | `id`, `isbn`, `title`, `publisher`, `author` (multivalorado), `genre` (multivalorado), `theme` (multivalorado) |
| **List** | Lista de obras criada por um usuário | `id`, `name`, `description`, `is_private` |
| **Review** | Avaliação de uma obra | `id`, `user_id`, `book_id`, `comment` (opcional), `rating` (1 a 5) |
| **Vote** | Like/dislike ou marcação em um conteúdo | `id`, `user_id`, `target_id`, `target_entity`, `status` |
| **Report** | Denúncia de conteúdo | `id`, `user_id`, `target_id`, `target_entity`, `description` |
| **User_List**, **Book_List**, **List_Review** | Tabelas associativas (N:N) | chaves estrangeiras das entidades relacionadas |

## Como o DER aparece no código

| Entidade | Entidade de domínio | Tabela (Alembic/SQLAlchemy) | Exposta na API |
| --- | --- | --- | --- |
| User | ✅ `domain/entities/user.py` | 🔜 | ✅ `/auth/*` |
| Book | ✅ `domain/entities/book.py` | ✅ `books`, `authors`, `book_author` | ✅ `/books` |
| List | ✅ `domain/entities/book_list.py` | 🔜 | ✅ `/lists` |
| Review / Vote / Report | 🔜 | 🔜 | 🔜 |

> Na implementação atual, o autor é normalizado em uma tabela própria (`authors`) ligada a `books` por `book_author`; gênero e tema ainda não têm tabela.
