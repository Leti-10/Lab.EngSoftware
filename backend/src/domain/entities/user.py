from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    id: int = field(init=False)
    username: str
    email: str
    password: str
    role: str = field(default="user")
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.username:
            raise ValueError("Username não pode ser vazio")

        if len(self.username) < 3:
            raise ValueError("Username deve ter pelo menos 3 caracteres")

        if not self.email:
            raise ValueError("Email não pode ser vazio")

        if not self.email or "@" not in self.email:
            raise ValueError("E-mail inválido")

        if not self.password:
            raise ValueError("Password não pode ser vazio")
