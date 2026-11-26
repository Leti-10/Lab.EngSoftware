from src.domain.entities import BookList
from src.domain.repositories import BookListRepository


class InMemoryBookListRepository(BookListRepository):
    def __init__(self) -> None:
        self.id = 0
        self.all_book_list: dict[int, BookList] = {}

    async def save(self, book_list: BookList) -> BookList:
        self.id += 1
        book_list.id = self.id
        self.all_book_list[self.id] = book_list
        return book_list

    async def update(self, book_list: BookList) -> BookList | None:
        if book_list.id not in self.all_book_list:
            return None
        self.all_book_list[book_list.id] = book_list
        return book_list

    async def get_by_id(self, list_id: int) -> BookList | None:
        return self.all_book_list.get(list_id, None)

    async def get_by_name(self, name: str) -> BookList | None:
        for _, book_list in self.all_book_list.items():
            if book_list.name.lower() == name.lower():
                return book_list
        return None

    async def delete(self, list_id: int) -> bool:
        if list_id in self.all_book_list:
            del self.all_book_list[list_id]
            return True
        return False

    async def list_by_owner(self, owner_id: int) -> list[BookList]:
        return [bl for bl in self.all_book_list.values() if bl.owner == owner_id]
