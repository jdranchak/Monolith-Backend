from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from common.db import SessionLocal
from models.db_models import User, Role
from models.schema import UserCreate, UserRead, UserWithRoles
import hashlib

router = APIRouter(prefix="/users")

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()

def hash_password(password: str) -> str:
    """Simple password hashing (in production, use bcrypt or similar)"""
    return hashlib.sha256(password.encode()).hexdigest()

@router.post("/", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username already exists
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(400, "Username already exists")
    
    # Check if email already exists
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email already exists")
    
    new_user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        title=payload.title,
        is_active=True  # New users are active by default
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return users

@router.get("/{id}", response_model=UserRead)
def get_user(id: int, db: Session = Depends(get_db)):
    """Get a specific user"""
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.get("/{id}/with-roles", response_model=UserWithRoles)
def get_user_with_roles(id: int, db: Session = Depends(get_db)):
    """Get user with all their roles"""
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/{user_id}/roles/{role_id}")
def assign_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Assign a role to a user"""
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    
    # Check if user already has this role
    if role in user.roles:
        raise HTTPException(400, f"User already has role '{role.name}'")
    
    user.roles.append(role)
    db.commit()
    
    return {"message": f"Role '{role.name}' assigned to user '{user.username}'"}

@router.delete("/{user_id}/roles/{role_id}")
def remove_role_from_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Remove a role from a user"""
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    role = db.query(Role).get(role_id)
    if not role:
        raise HTTPException(404, "Role not found")
    
    # Check if user has this role
    if role not in user.roles:
        raise HTTPException(400, f"User does not have role '{role.name}'")
    
    user.roles.remove(role)
    db.commit()
    
    return {"message": f"Role '{role.name}' removed from user '{user.username}'"}

@router.put("/{id}/activate")
def activate_user(id: int, db: Session = Depends(get_db)):
    """Activate a user account"""
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(404, "User not found")
    
    user.is_active = True
    db.commit()
    
    return {"message": f"User '{user.username}' activated"}

@router.put("/{id}/deactivate")
def deactivate_user(id: int, db: Session = Depends(get_db)):
    """Deactivate a user account"""
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(404, "User not found")
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User '{user.username}' deactivated"} 