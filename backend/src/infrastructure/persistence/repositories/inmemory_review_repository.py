from src.domain.entities import Book, Review, User
from src.domain.enums.enums import EnumReviewSort
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
        self.like_counts: dict[int, int] = {}

    async def save(self, review: Review) -> Review:
        if review.id is None:
            review.id = self._next_id
            self._next_id += 1
        self.reviews[review.id] = review
        return review

    async def get_by_id(self, review_id: int) -> Review | None:
        return self.reviews.get(review_id)

    async def update(self, review: Review) -> Review | None:
        if review.id is None or review.id not in self.reviews:
            return None
        self.reviews[review.id] = review
        return review

    async def find_by_filter(
        self,
        rating: int | None = None,
        username: str | None = None,
        book_title: str | None = None,
        comment: str | None = None,
        book_id: int | None = None,
        user_id: int | None = None,
    ) -> list[Review | None]:
        results = []
        for review in self.reviews.values():
            if rating is not None and review.rating != rating:
                continue
            if book_id is not None and review.book_id != book_id:
                continue
            if user_id is not None and review.user_id != user_id:
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

    async def get_all(self, order_by: str | None = None) -> list[Review]:
        reviews = list(self.reviews.values())
        if order_by == "rating":
            reviews.sort(key=lambda review: review.rating, reverse=True)
        elif order_by == "created_at":
            reviews.sort(key=lambda review: review.created_at, reverse=True)
        else:
            reviews.sort(key=lambda review: review.id or 0)
        return reviews

    async def get_page(
        self, page: int, page_size: int, sort_by: EnumReviewSort
    ) -> tuple[list[Review], int]:
        reviews = list(self.reviews.values())
        if sort_by == EnumReviewSort.POPULAR:
            reviews.sort(
                key=lambda review: (
                    self.like_counts.get(review.id or 0, 0),
                    review.created_at,
                    review.id or 0,
                ),
                reverse=True,
            )
        else:
            reviews.sort(
                key=lambda review: (review.created_at, review.id or 0),
                reverse=True,
            )

        total = len(reviews)
        start = (page - 1) * page_size
        return reviews[start : start + page_size], total
