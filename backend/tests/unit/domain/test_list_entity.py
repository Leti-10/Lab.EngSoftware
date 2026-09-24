import pytest

from src.domain.entities import DataList
from src.domain.exceptions import ListNameTooShortError, InvalidListOwnerError


def test_create_list_successfully():

    owner = 1
    name = "my_list"
    description = "generic_list_of_books"
    private = True
    books = [1, 2]

    new_list = DataList(owner, name, description, private, books)

    assert new_list.owner == owner
    assert new_list.name == name
    assert new_list.description == description
    assert new_list.private is private
    assert new_list.books == books


def test_should_not_create_list_with_short_name():
    with pytest.raises(ListNameTooShortError):
        DataList(owner=1, name="ab", description="desc", private=True, books=[])


def test_should_not_create_list_without_owner():
    with pytest.raises(InvalidListOwnerError):
        DataList(owner=None, name="generic", description="desc", private=True, books=[])
