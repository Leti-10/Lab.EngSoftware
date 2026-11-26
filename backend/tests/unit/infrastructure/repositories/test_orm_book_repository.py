import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.domain.entities import Book
from src.infrastructure.persistence.models import BookModelSQLAlchemy
from src.infrastructure.persistence.repositories import SQLAlchemyRepository


def make_book(
    *,
    book_id: int | None = None,
    isbn: str,
    title: str,
    authors: list[str],
    genre: list[str],
    theme: list[str],
) -> Book:
    return Book(
        id=book_id,
        isbn=isbn,
        title=title,
        authors=authors,
        publisher="Editora Teste",
        genre=genre,
        theme=theme,
    )


@pytest.mark.asyncio
async def test_book_repository_crud_persists_all_book_fields(postgres_engine):
    async with postgres_engine.begin() as connection:
        await connection.run_sync(BookModelSQLAlchemy.metadata.create_all)

    session_factory = async_sessionmaker(postgres_engine, expire_on_commit=False)
    book_id = None
    async with session_factory() as session:
        repository = SQLAlchemyRepository(session)
        saved = await repository.save(
            make_book(
                isbn="9780000000001",
                title="Livro Original",
                authors=["Autora Original"],
                genre=["Fantasia"],
                theme=["Amizade"],
            )
        )

        assert saved.id is not None
        book_id = saved.id
        assert saved.authors == ["Autora Original"]
        assert saved.genre == ["Fantasia"]
        assert saved.theme == ["Amizade"]
        assert await repository.get_by_id(saved.id) == saved
        assert await repository.get_by_isbn(saved.isbn) == saved
        assert await repository.get_all() == [saved]

        updated = await repository.update(
            make_book(
                book_id=saved.id,
                isbn="9780000000001",
                title="Livro Atualizado",
                authors=["Nova Autora"],
                genre=["Drama"],
                theme=["Memória"],
            )
        )

        assert updated.id == saved.id
        assert updated.title == "Livro Atualizado"
        assert updated.authors == ["Nova Autora"]
        assert updated.genre == ["Drama"]
        assert updated.theme == ["Memória"]

    assert book_id is not None
    async with session_factory() as session:
        repository = SQLAlchemyRepository(session)
        assert await repository.delete(book_id) is True
        assert await repository.delete(book_id) is False
        assert await repository.get_by_id(book_id) is None


@pytest.mark.asyncio
async def test_book_repository_filters_by_fields_and_combines_matches_with_or(
    postgres_engine,
):
    async with postgres_engine.begin() as connection:
        await connection.run_sync(BookModelSQLAlchemy.metadata.create_all)

    session_factory = async_sessionmaker(postgres_engine, expire_on_commit=False)
    async with session_factory() as session:
        repository = SQLAlchemyRepository(session)
        fantasy = await repository.save(
            make_book(
                isbn="9780000000002",
                title="Aventura Espacial",
                authors=["Ana Autora"],
                genre=["Fantasia"],
                theme=["Magia"],
            )
        )
        mystery = await repository.save(
            make_book(
                isbn="9780000000003",
                title="Mistério Antigo",
                authors=["Bruno Escritor"],
                genre=["Mistério"],
                theme=["Memória"],
            )
        )

        assert await repository.find_by_filter(isbn="0000000002") == [fantasy]
        assert await repository.find_by_filter(author="ana autor") == [fantasy]
        assert await repository.find_by_filter(genre="Fantasia") == [fantasy]
        assert await repository.find_by_filter(theme="Memória") == [mystery]
        assert await repository.find_by_filter() == []

        matches = await repository.find_by_filter(title="Aventura", author="Bruno")
        assert {book.id for book in matches if book is not None} == {
            fantasy.id,
            mystery.id,
        }
