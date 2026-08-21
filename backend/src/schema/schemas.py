from pydantic import BaseModel, EmailStr, ConfigDict

class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)

class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserListSchema(BaseModel):
    users: list[UserPublicSchema]

class TokenSchema(BaseModel):
    token_type: str
    access_token: str