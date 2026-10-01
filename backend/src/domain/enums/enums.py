from enum import Enum

class VoteTarget(str, Enum):
    LIST = "lists"
    BOOK = "books"
    REVIEW = "reviews"