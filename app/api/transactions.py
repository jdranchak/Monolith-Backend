from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db import SessionLocal
from models.db_models import Transaction, User
from models.schema import TransactionCreate, TransactionRead
from datetime import datetime

router = APIRouter(prefix="/transactions")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

@router.post("/", response_model=TransactionRead)
def create_transaction(payload: TransactionCreate, created_by_user_id: int, db: Session = Depends(get_db)):
    """Create a new financial transaction"""
    # Verify user exists
    user = db.query(User).get(created_by_user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    # Check if transaction number already exists
    if db.query(Transaction).filter(Transaction.transaction_number == payload.transaction_number).first():
        raise HTTPException(400, "Transaction number already exists")
    
    new_transaction = Transaction(
        transaction_number=payload.transaction_number,
        date=payload.date,
        description=payload.description,
        total_amount=payload.total_amount,
        created_by=created_by_user_id
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    
    return new_transaction

@router.get("/", response_model=list[TransactionRead])
def list_transactions(db: Session = Depends(get_db)):
    """Get all transactions"""
    transactions = db.query(Transaction).all()
    return transactions

@router.get("/{id}", response_model=TransactionRead)
def get_transaction(id: int, db: Session = Depends(get_db)):
    """Get a specific transaction"""
    transaction = db.query(Transaction).get(id)
    if not transaction:
        raise HTTPException(404, "Transaction not found")
    return transaction

@router.get("/by-user/{user_id}", response_model=list[TransactionRead])
def get_transactions_by_user(user_id: int, db: Session = Depends(get_db)):
    """Get all transactions created by a specific user"""
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    transactions = db.query(Transaction).filter(Transaction.created_by == user_id).all()
    return transactions

@router.get("/by-date-range/")
def get_transactions_by_date_range(
    start_date: str, 
    end_date: str, 
    db: Session = Depends(get_db)
):
    """Get transactions within a date range (YYYY-MM-DD format)"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(400, "Invalid date format. Use YYYY-MM-DD")
    
    transactions = db.query(Transaction).filter(
        Transaction.date >= start,
        Transaction.date <= end
    ).all()
    
    return transactions

@router.put("/{id}", response_model=TransactionRead)
def update_transaction(id: int, payload: TransactionCreate, db: Session = Depends(get_db)):
    """Update a transaction"""
    transaction = db.query(Transaction).get(id)
    if not transaction:
        raise HTTPException(404, "Transaction not found")
    
    # Check if new transaction number conflicts
    if payload.transaction_number != transaction.transaction_number:
        if db.query(Transaction).filter(Transaction.transaction_number == payload.transaction_number).first():
            raise HTTPException(400, "Transaction number already exists")
    
    transaction.transaction_number = payload.transaction_number
    transaction.date = payload.date
    transaction.description = payload.description
    transaction.total_amount = payload.total_amount
    
    db.commit()
    db.refresh(transaction)
    
    return transaction

@router.delete("/{id}")
def delete_transaction(id: int, db: Session = Depends(get_db)):
    """Delete a transaction"""
    transaction = db.query(Transaction).get(id)
    if not transaction:
        raise HTTPException(404, "Transaction not found")
    
    db.delete(transaction)
    db.commit()
    
    return {"message": f"Transaction {transaction.transaction_number} deleted successfully"} 