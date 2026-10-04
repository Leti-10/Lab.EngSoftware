from src.domain.entities import Book, Review, User
from src.domain.repositories import ReviewRepository


class InMemoryReviewRepository(ReviewRepository):
    def __init__(
        self,
        users: dict[int, User] | None = None,
        books: dict[int, Book] | None = None,
    ):
        self.reviews: dict[int, Review] = {}
        self.users = users or {}
        self.books = books or {}
        self._next_id = 1

    async def save(self, review: Review) -> Review:
        if review.id is None:
            review.id = self._next_id
            self._next_id += 1
        self.reviews[review.id] = review
        return review

    async def get_by_id(self, review_id: int) -> Review | None:
        return self.reviews.get(review_id)

    async def find_by_filter(
        self,
        rating: int | None = None,
        username: str | None = None,
        book_title: str | None = None,
        comment: str | None = None,
    ) -> list[Review]:
        results = []
        for review in self.reviews.values():
            if rating is not None and review.rating != rating:
                continue
            if username and (
                review.user_id not in self.users
                or username.casefold()
                not in self.users[review.user_id].username.casefold()
            ):
                continue
            if book_title and (
                review.book_id not in self.books
                or book_title.casefold()
                not in self.books[review.book_id].title.casefold()
            ):
                continue
            if comment and (
                review.comment is None or comment.lower() not in review.comment.lower()
            ):
                continue
            results.append(review)
        return results
