from pydantic import BaseModel, Field


class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=6)


class LoginSchema(BaseModel):
    email: str
    password: str


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    role: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponseSchema
