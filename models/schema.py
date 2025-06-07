from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class OrderRead(BaseModel):
    id: int
    product_name: str
    sale_price: float
    status: str
    sold_at: datetime
    
    class Config:
        from_attributes = True

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr

class CustomerRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    order_count: Optional[int] = 0
    # orders: Optional[List[OrderRead]] = []  # Commented out for now - can enable later
    
    class Config:
        from_attributes = True
