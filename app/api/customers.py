from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db import SessionLocal, engine
from models.db_models import Base, Customer, Order
from models.schema import CustomerCreate, CustomerRead, CustomerWithOrders

Base.metadata.create_all(bind=engine)  # temporary

router = APIRouter(prefix="/customers")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

@router.post("/", response_model=CustomerRead)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == payload.email).first():
        raise HTTPException(400, "Email exists")
    new = Customer(**payload.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.get("/{id}", response_model=CustomerRead)
def read_customer(id: int, db: Session = Depends(get_db)):
    cust = db.query(Customer).get(id)
    if not cust:
        raise HTTPException(404, "Not found")
    return cust

@router.get("/{id}/with-orders", response_model=CustomerWithOrders)
def read_customer_with_orders(id: int, db: Session = Depends(get_db)):
    """Get customer with all their orders included"""
    cust = db.query(Customer).get(id)
    if not cust:
        raise HTTPException(404, "Customer not found")
    return cust

@router.get("/", response_model=list[CustomerRead])
def list_customers(db: Session = Depends(get_db)):
    """Get all customers"""
    customers = db.query(Customer).all()
    return customers

# TODO: Uncomment when common/db.py, models/db_models.py, and models/schema.py are created 