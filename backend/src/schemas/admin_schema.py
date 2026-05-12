from pydantic import BaseModel, EmailStr


class AdminCreate(BaseModel):
    name: str 
    email: EmailStr
    is_superuser: bool = False

class AdminMessage(BaseModel):
    message: str