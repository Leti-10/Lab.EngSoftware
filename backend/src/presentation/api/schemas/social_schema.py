from datetime import datetime

from pydantic import BaseModel

from src.domain.enums.enums import EnumFollowTarget, EnumNotificationType
from src.presentation.api.schemas.book_list_schema import BookListResponseSchema
from src.presentation.api.schemas.book_schema import BookResponseSchema
from src.presentation.api.schemas.review_schema import ReviewResponseSchema


class CreateCommentSchema(BaseModel):
    text: str


class CommentResponseSchema(BaseModel):
    id: int
    review_id: int
    user_id: int
    username: str | None = None
    text: str
    created_at: datetime


class FollowStatusSchema(BaseModel):
    following: bool
    followers: int


class FollowItemSchema(BaseModel):
    target_type: EnumFollowTarget
    target_id: int


class PublicProfileSchema(BaseModel):
    id: int
    username: str
    bio: str | None = None
    avatar_url: str | None = None
    cover_url: str | None = None
    followers: int
    following: int
    is_following: bool


class PublicListsSchema(BaseModel):
    lists: list[BookListResponseSchema]


class NotificationResponseSchema(BaseModel):
    id: int
    type: EnumNotificationType
    actor_id: int
    actor_username: str | None = None
    review_id: int | None = None
    book_id: int | None = None
    read: bool
    created_at: datetime


class NotificationListSchema(BaseModel):
    items: list[NotificationResponseSchema]
    unread: int


class NotificationPreferenceSchema(BaseModel):
    likes: bool = True
    comments: bool = True
    follows: bool = True


class FeedItemSchema(ReviewResponseSchema):
    book_title: str | None = None


class RecommendationSchema(BaseModel):
    book: BookResponseSchema
    reason: str
