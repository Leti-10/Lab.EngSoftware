from enum import Enum

class EnumVoteTarget(str, Enum):
    LIST = "lists"
    BOOK = "books"
    REVIEW = "reviews"