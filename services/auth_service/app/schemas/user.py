from datetime import datetime
from uuid import UUID

from pydantic import  EmailStr
from pydantic import BaseModel
class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):

    email: EmailStr

    username: str

    password: str

    first_name: str

    last_name: str


class UserResponse(BaseModel):

    id: UUID

    email: EmailStr

    username: str

    first_name: str

    last_name: str

    role: str

    is_active: bool

    created_at: datetime


    class Config:
        from_attributes = True