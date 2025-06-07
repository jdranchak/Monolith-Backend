from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db import SessionLocal
from models.db_models import Product, Inventory, InventoryHistory
from models.schema import ProductCreate, ProductRead, InventoryRead, InventoryUpdate

router = APIRouter(prefix="/products")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

@router.post("/", response_model=ProductRead)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product and set initial inventory"""
    # Check if SKU already exists
    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise HTTPException(400, "SKU already exists")
    
    # Create product
    new_product = Product(
        name=payload.name,
        sku=payload.sku,
        price=payload.price,
        description=payload.description,
        quantity=payload.quantity  # This will be deprecated in favor of inventory table
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Create initial inventory record
    inventory = Inventory(
        product_id=new_product.id,
        quantity=payload.quantity,
        location="Main Warehouse"
    )
    db.add(inventory)
    
    # Create inventory history record
    history = InventoryHistory(
        product_id=new_product.id,
        old_quantity=0,
        new_quantity=payload.quantity,
        quantity_change=payload.quantity,
        change_reason="initial_stock",
        changed_by="system",
        notes="Initial product creation"
    )
    db.add(history)
    db.commit()
    
    return new_product

@router.get("/", response_model=list[ProductRead])
def list_products(db: Session = Depends(get_db)):
    """Get all products"""
    products = db.query(Product).all()
    return products

@router.get("/{id}", response_model=ProductRead)
def get_product(id: int, db: Session = Depends(get_db)):
    """Get a specific product"""
    product = db.query(Product).get(id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

@router.get("/{id}/inventory", response_model=InventoryRead)
def get_product_inventory(id: int, db: Session = Depends(get_db)):
    """Get current inventory for a product"""
    inventory = db.query(Inventory).filter(Inventory.product_id == id).first()
    if not inventory:
        raise HTTPException(404, "Inventory record not found")
    return inventory

@router.put("/{id}/inventory", response_model=InventoryRead)
def update_inventory(id: int, payload: InventoryUpdate, db: Session = Depends(get_db)):
    """Update product inventory and log the change"""
    # Get current inventory
    inventory = db.query(Inventory).filter(Inventory.product_id == id).first()
    if not inventory:
        raise HTTPException(404, "Inventory record not found")
    
    old_quantity = inventory.quantity
    new_quantity = payload.quantity
    
    # Update inventory
    inventory.quantity = new_quantity
    
    # Log the change
    history = InventoryHistory(
        product_id=id,
        old_quantity=old_quantity,
        new_quantity=new_quantity,
        quantity_change=new_quantity - old_quantity,
        change_reason=payload.change_reason,
        changed_by="api_user",  # In real app, get from auth
        notes=payload.notes
    )
    db.add(history)
    db.commit()
    db.refresh(inventory)
    
    return inventory 