from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.enums.enums import EnumFollowTarget, EnumNotificationType
from src.domain.exceptions.social import InvalidCommentError, InvalidFollowError

MAX_COMMENT_LENGTH = 500


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class Comment:
    id: int | None = field(default=None)
    review_id: int = field(default=0)
    user_id: int = field(default=0)
    text: str = field(default="")
    created_at: datetime = field(default_factory=_now)

    def __post_init__(self):
        self.text = (self.text or "").strip()
        if not self.text:
            raise InvalidCommentError("O comentário não pode ser vazio.")
        if len(self.text) > MAX_COMMENT_LENGTH:
            raise InvalidCommentError(
                f"O comentário deve ter no máximo {MAX_COMMENT_LENGTH} caracteres."
            )
        if self.review_id <= 0 or self.user_id <= 0:
            raise InvalidCommentError("Resenha ou usuário inválido.")


@dataclass
class Follow:
    id: int | None = field(default=None)
    follower_id: int = field(default=0)
    target_type: EnumFollowTarget | str = field(default="")
    target_id: int = field(default=0)
    created_at: datetime = field(default_factory=_now)

    def __post_init__(self):
        if not isinstance(self.target_type, EnumFollowTarget):
            try:
                self.target_type = EnumFollowTarget(self.target_type)
            except ValueError:
                raise InvalidFollowError("O tipo a seguir é inválido.") from None
        if self.follower_id <= 0 or self.target_id <= 0:
            raise InvalidFollowError("Usuário ou alvo inválido.")
        if (
            self.target_type == EnumFollowTarget.USER
            and self.follower_id == self.target_id
        ):
            raise InvalidFollowError("Você não pode seguir a si mesmo.")


@dataclass
class Notification:
    id: int | None = field(default=None)
    user_id: int = field(default=0)
    type: EnumNotificationType | str = field(default="")
    actor_id: int = field(default=0)
    review_id: int | None = field(default=None)
    book_id: int | None = field(default=None)
    read: bool = field(default=False)
    created_at: datetime = field(default_factory=_now)

    def __post_init__(self):
        if not isinstance(self.type, EnumNotificationType):
            self.type = EnumNotificationType(self.type)


@dataclass
class NotificationPreference:
    user_id: int = field(default=0)
    likes: bool = field(default=True)
    comments: bool = field(default=True)
    follows: bool = field(default=True)

    def allows(self, kind: EnumNotificationType) -> bool:
        return {
            EnumNotificationType.LIKE: self.likes,
            EnumNotificationType.COMMENT: self.comments,
            EnumNotificationType.FOLLOW: self.follows,
        }[kind]
