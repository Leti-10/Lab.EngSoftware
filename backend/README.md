# Servidor do projeto books

API provedora de serviços para a aplicação, desenvolvida em FastAPI seguindo os critérios fornecidos pelo professor Juan Hassan da disciplina Laboratório de Engenharia de Software pela Fatec de São José dos Campos.

## Sumário
- [Como Executar](#how_to_run)
- [Arquitetura da Aplicação](#app_architecture)
- [Diagrama de Entidade e Relacionamento](#der)
- [Rotas da Aplicação](#app_route)
- [Tecnologias Utilizadas](#technology)

## <span id="how_to_run"> ❓ Como Executar </span>
- Instruções de execução

## <span id="app_architecture"> Arquitetura da aplicação </span>
- Estrutura de diretórios e suas funções

## <span id="der"> Diagrama de Entidade e Relacionamento (DER) </span>
![DER](../img/der.png)

### Entidades
- User (Usuário do sistema)
  - ID (Identificador único) - Gerado automaticamente
  - Name (Nome) - Obrigatório
  - Email (Email) - Obrigatório
  - Password (Senha) - Obrigatório
  - Role (Comum, Desenvolvedor, Admin) - Apenas um admin pode modificar
  - Created_at (Data de criação) - Gerado automaticamente
- Book (Livros)
  - ID (Identificador único) - Gerado automaticamente
  - ISBN (ISBN do livro) - Opcional (um livro pode não ter o ISBN)
  - Genre (Gênero) - Multivalorado obrigatório
  - Theme (Tema) - Multivalorado obrigatório
  - Title (Título) - Obrigatório
  - Author (Autor) - Multivalorado obrigatório
  - Publisher (Editora) - Obrigatório
- List (Uma lista de livros criada pelo usuário)
  - ID (Identificador único) - Gerado automaticamente
  - Name (Nome) - Obrigatório
  - Description (Descrição breve) - Opcional
  - isPrivate (Indica se a lista é privada) - Opcional
- Review (Review de algum livro)
  - ID (Identificador único) - Gerado automaticamente
  - User_ID (ID do Usuário) - O front passa automaticamente
  - Book_ID (ID do Livro) - O front passa automaticamente
  - Comment (Comentário) - Opcional
  - Rating (Avaliação em estrelas) - Obrigatório (vai de 1 a 5)
- Vote (O usuário pode dar like/dislike ou adicionar marcações para livros)
  - ID (Identificador único) - Gerado automaticamente
  - User_ID (ID do Usuário) - O front passa automaticamente
  - Target_ID (ID do Alvo) - O front passa automaticamente
  - Target_Entity (Entidade do alvo) - O front passa automaticamente
  - Status (Indica o conteúdo do voto) - Obrigatório
- Report (O usuário pode reportar algum conteúdo)
  - ID (Identificador único) - Gerado automaticamente
  - User_ID (ID do Usuário) - O front passa automaticamente
  - Target_ID (ID do Alvo) - O front passa automaticamente
  - Target_Entity (Entidade do alvo) - O front passa automaticamente
  - Description (Descrição do motivo da denúncia) - Obrigatório

## <span id="app_route"> ↪️ Rotas da Aplicação </span>
- /

## <span id="technology"> 💻 Tecnologias Utilizadas </span>
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