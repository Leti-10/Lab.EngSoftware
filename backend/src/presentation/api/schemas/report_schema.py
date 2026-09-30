from pydantic import BaseModel

class CreateReportSchema(BaseModel):
    description: str
    user_id: int
    target_entity: str
    target_id: int
