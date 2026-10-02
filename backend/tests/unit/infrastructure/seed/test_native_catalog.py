from src.domain.entities import Book
from src.infrastructure.persistence.repositories import InMemoryBookRepository
from src.infrastructure.seed import NATIVE_BOOKS, seed_native_catalog


def test_all_native_books_are_valid_domain_entities():
    for item in NATIVE_BOOKS:
        Book(**item)


def test_native_books_have_unique_isbns():
    isbns = [item["isbn"] for item in NATIVE_BOOKS]

    assert len(isbns) == len(set(isbns))


def test_catalog_covers_books_mangas_and_comics():
    genres = {genre for item in NATIVE_BOOKS for genre in item["genre"]}

    assert {"Mangá", "Quadrinhos", "Romance"} <= genres


async def test_seed_adds_every_native_book():
    repository = InMemoryBookRepository()

    added = await seed_native_catalog(repository)

    assert added == len(NATIVE_BOOKS)
    assert len(await repository.find_by_filter()) == len(NATIVE_BOOKS)


async def test_seed_is_idempotent():
    repository = InMemoryBookRepository()
    await seed_native_catalog(repository)

    assert await seed_native_catalog(repository) == 0
    assert len(await repository.find_by_filter()) == len(NATIVE_BOOKS)


async def test_seed_keeps_books_registered_by_users():
    repository = InMemoryBookRepository()
    await repository.save(Book(**{**NATIVE_BOOKS[0], "title": "Edição da comunidade"}))

    await seed_native_catalog(repository)

    assert (await repository.get_by_isbn(NATIVE_BOOKS[0]["isbn"])).title == "Edição da comunidade"
