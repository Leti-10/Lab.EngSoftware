from dataclasses import dataclass, field

from src.domain.exceptions import InvalidListOwnerError, ListNameTooShortError


@dataclass
class DataList:
    id: int = field(init=False)
    owner: int = field(init=True)
    name: str = field(default="")
    description: str = field(default="")
    private: bool = field(default=False)
    books: list[int] = field(default_factory=list[int])

    def __post_init__(self):
        if self.owner is None:
            raise InvalidListOwnerError("''")

        if not self.name or len(self.name) < 3:
            raise ListNameTooShortError("Name deve ter pelo menos 1 caracteres")

        if not self.description or len(self.description) < 1:
            raise ValueError("Description deve ter pelo menos 1 caracteres")
