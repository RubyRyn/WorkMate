from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    picture: str | None
    role: str

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
