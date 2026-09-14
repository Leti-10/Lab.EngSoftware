import pytest
from src.domain.entities.book import Book


@pytest.mark.parametrize(
    "isbn, genre, theme, title, author, publisher, expected_error",
    [
        (
            "852203142X",
            ["Ficção"],
            ["Clássicos"],
            "O Pequeno Príncipe",
            [],
            "Editora Agir",
            "Author deve ter pelo menos 1 caracteres",
        ),
        (
            "1234567",
            ["Ficção Científica"],
            [],
            "O Programador",
            ["Letícia"],
            "Editora Tech",
            "ISBN deve ter no mínimo 10 dígitos",
        ),
        (
            "9788522031429",
            ["Romance", "Drama"],
            ["Superação"],
            "",
            [],
            "Editora Exemplo",
            "Title deve ter pelo menos 1 caracteres",
        ),
    ],
)
def test_should_raise_error_when_book_data_is_invalid(
    isbn, genre, theme, title, author, publisher, expected_error
):
    with pytest.raises(ValueError, match=expected_error):
        Book(
            isbn=isbn,
            genre=genre,
            theme=theme,
            title=title,
            author=author,
            publisher=publisher,
        )
