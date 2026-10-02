from src.domain.entities import Review
from src.domain.repositories import ReviewRepository


class InMemoryReviewRepository(ReviewRepository):
    def __init__(self):
        self.reviews: dict[int, Review] = {}
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
        user_id: int | None = None,
        book_id: int | None = None,
        comment: str | None = None,
    ) -> list[Review]:
        results = []
        for review in self.reviews.values():
            if rating is not None and review.rating != rating:
                continue
            if user_id is not None and review.user_id != user_id:
                continue
            if book_id is not None and review.book_id != book_id:
                continue
            if comment and (review.comment is None or comment.lower() not in review.comment.lower()):
                continue
            results.append(review)
        return results