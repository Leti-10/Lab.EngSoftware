from dataclasses import dataclass, field
from datetime import datetime, timezone

MAX_BIO_LENGTH = 300
MAX_URL_LENGTH = 500


@dataclass
class User:
    id: int = field(init=False)
    username: str
    email: str
    password: str
    role: str = field(default="user")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    bio: str | None = field(default=None)
    avatar_url: str | None = field(default=None)
    cover_url: str | None = field(default=None)

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

    def update_profile(
        self,
        bio: str | None,
        avatar_url: str | None,
        cover_url: str | None,
    ) -> None:
        bio = (bio or "").strip() or None
        avatar_url = (avatar_url or "").strip() or None
        cover_url = (cover_url or "").strip() or None

        if bio is not None and len(bio) > MAX_BIO_LENGTH:
            raise ValueError(f"A bio deve ter no máximo {MAX_BIO_LENGTH} caracteres")

        for label, url in (("avatar", avatar_url), ("capa", cover_url)):
            if url is None:
                continue
            if len(url) > MAX_URL_LENGTH:
                raise ValueError(f"A URL do {label} é longa demais")
            if not url.lower().startswith(("http://", "https://")):
                raise ValueError(
                    f"A URL do {label} deve começar com http:// ou https://"
                )

        self.bio = bio
        self.avatar_url = avatar_url
        self.cover_url = cover_url
