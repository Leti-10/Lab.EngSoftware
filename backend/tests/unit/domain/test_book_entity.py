import pytest
from datetime import datetime
from src.domain.entities.book import Book


@pytest.mark.parametrize(
    "isbn, genre, theme, title, author, publisher, expected_error",
    [
        (
            "1234567890123",
            ["Fiction"],
            ["Histórias inspiradoras"],
            "Aventuras da Capivara",
            ["Fabio Nawa"],
            "Editora Fatec",
            None,
        ),
        (
            "852203142X",
            ["Ficção"],
            ["Clássicos"],
            "O Pequeno Príncipe",
            [],
            "Editora Agir",
            None,
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
            id=1,
            isbn=isbn,
            genre=genre,
            theme=theme,
            title=title,
            author=author,
            publisher=publisher,
        )
