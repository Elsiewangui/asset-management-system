# FastAPI routing tools
from fastapi import APIRouter, Depends, HTTPException

# Database session
from sqlalchemy.orm import Session

# Database dependency
from database import get_db

# Models and schemas
from models import User, AssetAssignment
from schemas import UserCreate, UserResponse, UserUpdate, AssignmentResponse

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

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get one user by ID
    """

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    updated_user: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information
    """

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.username = updated_user.username
    user.email = updated_user.email
    user.department = updated_user.department
    user.role = updated_user.role

    db.commit()
    db.refresh(user)

    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete user
    """

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }

# GET ALL ASSETS ASSIGNED TO A USER
@router.get("/{user_id}/assignments")
def get_user_assignments(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Return all assignments for a user
    """

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    assignments = db.query(AssetAssignment).filter(
        AssetAssignment.user_id == user_id
    ).all()

    return assignments

@router.get(
    "/{user_id}/assignments",
    response_model=list[AssignmentResponse]
)
def get_user_assignments(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Return all assignments for a user
    """

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    assignments = db.query(AssetAssignment).filter(
        AssetAssignment.user_id == user_id
    ).all()

    return assignments