from pydantic import BaseModel, Field


class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=6)


class LoginSchema(BaseModel):
    email: str
    password: str


class UpdateProfileSchema(BaseModel):
    bio: str | None = None
    avatar_url: str | None = None
    cover_url: str | None = None


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    role: str
    bio: str | None = None
    avatar_url: str | None = None
    cover_url: str | None = None


class AuthResponseSchema(BaseModel):
    user: UserResponseSchema
