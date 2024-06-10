from pydantic import BaseModel, EmailStr, Field
import datetime

class ContactInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: datetime.date
    other: str = Field(default='None')
    
class ContactOutput(ContactInput):
    id: int = 1
    
    class Config:
        from_attributes = True
        