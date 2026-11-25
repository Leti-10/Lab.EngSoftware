from enum import Enum


class EnumVoteTarget(str, Enum):
    LIST = "lists"
    BOOK = "books"
    REVIEW = "reviews"


class EnumReadingStatus(str, Enum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    READ = "read"


class EnumFollowTarget(str, Enum):
    USER = "users"
    LIST = "lists"


class EnumNotificationType(str, Enum):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
