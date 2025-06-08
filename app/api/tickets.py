from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db import SessionLocal
from models.db_models import Ticket, Customer, Employee
from models.schema import TicketCreate, TicketRead
from datetime import datetime

router = APIRouter(prefix="/tickets")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

@router.post("/", response_model=TicketRead)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    """Create a new support ticket"""
    # Verify customer exists
    customer = db.query(Customer).get(payload.customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    
    # Verify assigned employee exists (if provided)
    if payload.assigned_to:
        employee = db.query(Employee).get(payload.assigned_to)
        if not employee:
            raise HTTPException(404, "Employee not found")
    
    # Check if ticket number already exists
    if db.query(Ticket).filter(Ticket.ticket_number == payload.ticket_number).first():
        raise HTTPException(400, "Ticket number already exists")
    
    new_ticket = Ticket(
        ticket_number=payload.ticket_number,
        customer_id=payload.customer_id,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
        status="open",  # New tickets start as open
        assigned_to=payload.assigned_to
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    
    return new_ticket

@router.get("/", response_model=list[TicketRead])
def list_tickets(db: Session = Depends(get_db)):
    """Get all tickets"""
    tickets = db.query(Ticket).all()
    return tickets

@router.get("/{id}", response_model=TicketRead)
def get_ticket(id: int, db: Session = Depends(get_db)):
    """Get a specific ticket"""
    ticket = db.query(Ticket).get(id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return ticket

@router.get("/by-customer/{customer_id}", response_model=list[TicketRead])
def get_tickets_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get all tickets for a specific customer"""
    customer = db.query(Customer).get(customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    
    tickets = db.query(Ticket).filter(Ticket.customer_id == customer_id).all()
    return tickets

@router.get("/by-status/{status}", response_model=list[TicketRead])
def get_tickets_by_status(status: str, db: Session = Depends(get_db)):
    """Get all tickets with a specific status"""
    valid_statuses = ["open", "in_progress", "resolved", "closed"]
    if status not in valid_statuses:
        raise HTTPException(400, f"Status must be one of: {valid_statuses}")
    
    tickets = db.query(Ticket).filter(Ticket.status == status).all()
    return tickets

@router.get("/by-priority/{priority}", response_model=list[TicketRead])
def get_tickets_by_priority(priority: str, db: Session = Depends(get_db)):
    """Get all tickets with a specific priority"""
    valid_priorities = ["low", "medium", "high", "urgent"]
    if priority not in valid_priorities:
        raise HTTPException(400, f"Priority must be one of: {valid_priorities}")
    
    tickets = db.query(Ticket).filter(Ticket.priority == priority).all()
    return tickets

@router.put("/{id}/status")
def update_ticket_status(id: int, status: str, db: Session = Depends(get_db)):
    """Update ticket status"""
    ticket = db.query(Ticket).get(id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    
    valid_statuses = ["open", "in_progress", "resolved", "closed"]
    if status not in valid_statuses:
        raise HTTPException(400, f"Status must be one of: {valid_statuses}")
    
    ticket.status = status
    
    # Set resolved_at when ticket is resolved
    if status == "resolved":
        ticket.resolved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Ticket {ticket.ticket_number} status updated to {status}"}

@router.put("/{id}/assign/{employee_id}")
def assign_ticket(id: int, employee_id: int, db: Session = Depends(get_db)):
    """Assign ticket to an employee"""
    ticket = db.query(Ticket).get(id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    
    employee = db.query(Employee).get(employee_id)
    if not employee:
        raise HTTPException(404, "Employee not found")
    
    ticket.assigned_to = employee_id
    db.commit()
    
    return {"message": f"Ticket {ticket.ticket_number} assigned to employee {employee_id}"}

@router.put("/{id}/unassign")
def unassign_ticket(id: int, db: Session = Depends(get_db)):
    """Remove assignment from ticket"""
    ticket = db.query(Ticket).get(id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    
    ticket.assigned_to = None
    db.commit()
    
    return {"message": f"Ticket {ticket.ticket_number} unassigned"}

@router.delete("/{id}")
def delete_ticket(id: int, db: Session = Depends(get_db)):
    """Delete a ticket"""
    ticket = db.query(Ticket).get(id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    
    db.delete(ticket)
    db.commit()
    
    return {"message": f"Ticket {ticket.ticket_number} deleted successfully"} 