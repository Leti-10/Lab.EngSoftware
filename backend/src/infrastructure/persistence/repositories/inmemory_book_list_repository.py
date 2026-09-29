from src.domain.entities import BookList
from src.domain.repositories import BookListRepository


class InMemoryBookListRepository(BookListRepository):
    def __init__(self):
        self.id = 0
        self.all_book_list: dict[int, BookList] = {}

    def save(self, book_list: BookList) -> BookList:
        self.id += 1
        book_list.id = self.id
        self.all_book_list[self.id] = book_list
        return book_list

    def get_by_id(self, list_id: int) -> BookList | None:
        return self.all_book_list.get(list_id, None)

    def get_by_name(self, name: str) -> BookList | None:
        for _, book_list in self.all_book_list.items():
            if book_list.name.lower() == name.lower():
                return book_list
        return None

    def delete(self, list_id: int) -> bool:
        if list_id in self.all_book_list:
            del self.all_book_list[list_id]
            return True
        return False
