from src.domain.repositories import BookListRepository

class DeleteBookListUseCase:
    def __init__(self, book_list_repository: BookListRepository):
        self.book_list_repository = book_list_repository

    async def execute(self, list_id: int, user_id: int) -> None:
        book_list = self.book_list_repository.get_by_id(list_id)
        if book_list is None:
            raise ValueError("Lista não encontrada")

        if book_list.owner != user_id:
            raise ValueError("Você não é o proprietário desta lista")

        self.book_list_repository.delete(list_id)