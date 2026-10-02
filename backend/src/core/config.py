import os


class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-secret-change-me-please-0123456789")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
