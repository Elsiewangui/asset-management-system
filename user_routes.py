# FastAPI routing tools
from fastapi import APIRouter, Depends, HTTPException

# Database session
from sqlalchemy.orm import Session

# Database dependency
from database import get_db

# Models and schemas
from models import User
from schemas import UserCreate, UserResponse

# User router
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Create new user
@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    new_user = User(
        username=user.username,
        email=user.email,
        department=user.department,
        role=user.role,

        # temporary placeholder
        password_hash=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# GET ALL USERS
@router.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """
    Return all users
    """

    users = db.query(User).all()

    return users