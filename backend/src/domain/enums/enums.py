from enum import Enum

class ReportTarget(str, Enum):
    USER = "users"
    LIST = "lists"
    REVIEW = "reviews"
    BOOK = "books"