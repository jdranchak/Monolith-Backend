from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db import SessionLocal
from models.db_models import Order, Customer, Product, Inventory, InventoryHistory
from models.schema import OrderCreate, OrderRead

router = APIRouter(prefix="/orders")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

@router.post("/", response_model=OrderRead)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order and update inventory"""
    # Verify customer exists
    customer = db.query(Customer).get(payload.customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    
    # Verify product exists
    product = db.query(Product).get(payload.product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    
    # Check inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == payload.product_id).first()
    if not inventory or inventory.quantity < 1:
        raise HTTPException(400, "Product out of stock")
    
    # Use product price if no sale price provided
    sale_price = payload.sale_price if payload.sale_price else product.price
    
    # Create order
    new_order = Order(
        customer_id=payload.customer_id,
        product_id=payload.product_id,
        product_name=product.name,
        sale_price=sale_price,
        status="pending"
    )
    db.add(new_order)
    
    # Update inventory (reduce by 1)
    old_quantity = inventory.quantity
    inventory.quantity -= 1
    
    # Log inventory change
    history = InventoryHistory(
        product_id=payload.product_id,
        old_quantity=old_quantity,
        new_quantity=inventory.quantity,
        quantity_change=-1,
        change_reason="sale",
        changed_by="order_system",
        notes=f"Order #{new_order.id} created"
    )
    db.add(history)
    
    # Update customer order count
    customer.order_count += 1
    
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("/", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    """Get all orders"""
    orders = db.query(Order).all()
    return orders

@router.get("/by-status/{status}", response_model=list[OrderRead])
def get_orders_by_status(status: str, db: Session = Depends(get_db)):
    """Get all orders with a specific status"""
    valid_statuses = ["pending", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(400, f"Status must be one of: {valid_statuses}")
    
    orders = db.query(Order).filter(Order.status == status).all()
    return orders

@router.get("/by-customer/{customer_id}", response_model=list[OrderRead])
def get_orders_by_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get all orders for a specific customer"""
    customer = db.query(Customer).get(customer_id)
    if not customer:
        raise HTTPException(404, "Customer not found")
    
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return orders

@router.get("/{id}", response_model=OrderRead)
def get_order(id: int, db: Session = Depends(get_db)):
    """Get a specific order"""
    order = db.query(Order).get(id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order

@router.put("/{id}/status")
def update_order_status(id: int, status: str, db: Session = Depends(get_db)):
    """Update order status (pending, completed, cancelled)"""
    order = db.query(Order).get(id)
    if not order:
        raise HTTPException(404, "Order not found")
    
    valid_statuses = ["pending", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(400, f"Status must be one of: {valid_statuses}")
    
    order.status = status
    db.commit()
    
    return {"message": f"Order {id} status updated to {status}"} 