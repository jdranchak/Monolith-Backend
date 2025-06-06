from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr

class CustomerRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True
