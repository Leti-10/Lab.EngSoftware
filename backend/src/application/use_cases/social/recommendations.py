from dataclasses import dataclass

from src.domain.entities import Book
from src.domain.enums.enums import EnumReadingStatus
from src.domain.repositories import BookRepository, ReadingRepository
from src.domain.repositories.review_repository import ReviewRepository

READING_WEIGHT = {
    EnumReadingStatus.READ: 0.8,
    EnumReadingStatus.READING: 0.8,
    EnumReadingStatus.WANT_TO_READ: 0.5,
}
AUTHOR_BONUS = 2.0
MIN_LIKED_RATING = 4


@dataclass
class Recommendation:
    book: Book
    reason: str


def _authors(book: Book) -> list[str]:
    return [book.authors] if isinstance(book.authors, str) else list(book.authors)


class RecommendBooksUseCase:
    def __init__(
        self,
        review_repository: ReviewRepository,
        reading_repository: ReadingRepository,
        book_repository: BookRepository,
    ):
        self.review_repository = review_repository
        self.reading_repository = reading_repository
        self.book_repository = book_repository

    async def execute(self, user_id: int, limit: int = 10) -> list[Recommendation]:
        reviews = await self.review_repository.find_by_filter(user_id=user_id)
        readings = await self.reading_repository.find_by_user(user_id)

        weights: dict[int, float] = {}
        for review in reviews:
            if review:
                if review.rating >= MIN_LIKED_RATING:
                    weights[review.book_id] = max(
                        weights.get(review.book_id, 0), review.rating / 5
                    )
        for reading in readings:
            status = EnumReadingStatus(reading.status)
            weights[reading.book_id] = max(
                weights.get(reading.book_id, 0), READING_WEIGHT[status]
            )
        seen = {review.book_id for review in reviews if review} | {
            reading.book_id for reading in readings
        }

        genre_weight: dict[str, float] = {}
        author_weight: dict[str, float] = {}
        for book_id, weight in weights.items():
            book = await self.book_repository.get_by_id(book_id)
            if book is None:
                continue
            for genre in book.genre:
                genre_weight[genre] = genre_weight.get(genre, 0) + weight
            for author in _authors(book):
                author_weight[author] = author_weight.get(author, 0) + weight

        scored: list[tuple[float, int, Recommendation]] = []
        for book in await self.book_repository.get_all():
            if book is None or book.id in seen:
                continue
            author_hits = [a for a in _authors(book) if a in author_weight]
            genre_hits = [g for g in book.genre if g in genre_weight]
            score = AUTHOR_BONUS * sum(author_weight[a] for a in author_hits) + sum(
                genre_weight[g] for g in genre_hits
            )
            if score <= 0:
                continue
            if author_hits:
                reason = f"Porque você gosta de {author_hits[0]}"
            else:
                best = max(genre_hits, key=lambda g: genre_weight[g])
                reason = f"Porque você curte {best}"
            if book.id:
                scored.append((score, book.id, Recommendation(book, reason)))

        scored.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in scored[:limit]]
