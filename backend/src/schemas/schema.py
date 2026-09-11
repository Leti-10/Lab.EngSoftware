from pydantic import BaseModel


class TokenSchema(BaseModel):
    token_type: str
    access_token: str
