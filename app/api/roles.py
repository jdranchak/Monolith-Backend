from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db import SessionLocal
from models.db_models import Role, User
from models.schema import RoleCreate, RoleRead, RoleWithUsers

router = APIRouter(prefix="/roles")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

@router.post("/", response_model=RoleRead)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role"""
    # Check if role name already exists
    if db.query(Role).filter(Role.name == payload.name).first():
        raise HTTPException(400, "Role name already exists")
    
    new_role = Role(
        name=payload.name,
        permissions=payload.permissions
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return new_role

@router.get("/", response_model=list[RoleRead])
def list_roles(db: Session = Depends(get_db)):
    """Get all roles"""
    roles = db.query(Role).all()
    return roles

@router.get("/{id}", response_model=RoleRead)
def get_role(id: int, db: Session = Depends(get_db)):
    """Get a specific role"""
    role = db.query(Role).get(id)
    if not role:
        raise HTTPException(404, "Role not found")
    return role

@router.get("/{id}/with-users", response_model=RoleWithUsers)
def get_role_with_users(id: int, db: Session = Depends(get_db)):
    """Get role with all users who have this role"""
    role = db.query(Role).get(id)
    if not role:
        raise HTTPException(404, "Role not found")
    return role

@router.put("/{id}", response_model=RoleRead)
def update_role(id: int, payload: RoleCreate, db: Session = Depends(get_db)):
    """Update a role's permissions"""
    role = db.query(Role).get(id)
    if not role:
        raise HTTPException(404, "Role not found")
    
    # Check if new name conflicts with existing role
    if payload.name != role.name:
        if db.query(Role).filter(Role.name == payload.name).first():
            raise HTTPException(400, "Role name already exists")
    
    role.name = payload.name
    role.permissions = payload.permissions
    db.commit()
    db.refresh(role)
    
    return role

@router.delete("/{id}")
def delete_role(id: int, db: Session = Depends(get_db)):
    """Delete a role (only if no users have it)"""
    role = db.query(Role).get(id)
    if not role:
        raise HTTPException(404, "Role not found")
    
    # Check if any users have this role
    if role.users:
        raise HTTPException(400, f"Cannot delete role '{role.name}' - {len(role.users)} users still have this role")
    
    db.delete(role)
    db.commit()
    
    return {"message": f"Role '{role.name}' deleted successfully"} 