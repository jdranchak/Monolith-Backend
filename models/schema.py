from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Product schemas
class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float
    description: Optional[str] = None
    quantity: int

class ProductRead(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    description: Optional[str] = None
    quantity: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Order schemas
class OrderCreate(BaseModel):
    product_id: int
    customer_id: int
    sale_price: Optional[float] = None  # If None, use product price

class OrderRead(BaseModel):
    id: int
    product_name: str
    sale_price: float
    status: str
    sold_at: datetime
    customer_id: int
    product_id: int
    
    class Config:
        from_attributes = True

# Customer schemas
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr

class CustomerRead(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    order_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

# Enhanced customer with orders
class CustomerWithOrders(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    order_count: Optional[int] = 0
    orders: List[OrderRead] = []
    
    class Config:
        from_attributes = True

# Inventory schemas
class InventoryRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    location: str
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InventoryUpdate(BaseModel):
    quantity: int
    change_reason: str
    notes: Optional[str] = None

# Role schemas
class RoleRead(BaseModel):
    id: int
    name: str
    permissions: Optional[dict] = None
    
    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    name: str
    permissions: Optional[dict] = None

# User schemas (for future use)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: str

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# User with roles included
class UserWithRoles(BaseModel):
    id: int
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    roles: List[RoleRead] = []
    
    class Config:
        from_attributes = True

# Role with users included
class RoleWithUsers(BaseModel):
    id: int
    name: str
    permissions: Optional[dict] = None
    users: List[UserRead] = []
    
    class Config:
        from_attributes = True

# Transaction schemas (for future use)
class TransactionCreate(BaseModel):
    transaction_number: str
    date: datetime
    description: Optional[str] = None
    total_amount: float

class TransactionRead(BaseModel):
    id: int
    transaction_number: str
    date: datetime
    description: Optional[str] = None
    total_amount: float
    created_by: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Ticket schemas (for future use)
class TicketCreate(BaseModel):
    ticket_number: str
    customer_id: int
    subject: str
    description: str
    priority: str = "medium"
    assigned_to: Optional[int] = None

class TicketRead(BaseModel):
    id: int
    ticket_number: str
    customer_id: int
    subject: str
    description: str
    priority: str
    status: str
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
