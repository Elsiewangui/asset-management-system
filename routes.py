
# FastAPI tools for routing
from fastapi import APIRouter, Depends, HTTPException
from datetime import date

# SQLAlchemy session (to talk to database)
from sqlalchemy.orm import Session

# Import database session generator
from database import get_db

# Import your table model
from models import Asset,User, AssetAssignment
from schemas import AssetCreate, AssetResponse, UserResponse, UserCreate, AssignmentCreate, AssignmentResponse

# Create router object (this holds all our endpoints)
router = APIRouter(
    prefix="/assets",  # all routes will start with /assets
    tags=["Assets"]    # groups them in Swagger UI
)

# CREATE ASSET (POST)
@router.post("/", response_model=AssetResponse)
def create_asset(asset: AssetCreate, db: Session = Depends(get_db)):
    """
    This function adds a new asset to the database
    """

    # Convert input data into database model
    new_asset = Asset(**asset.dict())

    # Add to database session
    db.add(new_asset)

    # Save changes
    db.commit()

    # Refresh to get updated data (like ID)
    db.refresh(new_asset)

    return new_asset



# GET ALL ASSETS (READ)
@router.get("/", response_model=list[AssetResponse])
def get_assets(db: Session = Depends(get_db)):
    """
    This function returns all assets in the database
    """

    # Query all assets
    assets = db.query(Asset).all()

    return assets

# CREATE ASSIGNMENT
@router.post("/assignments", response_model=AssignmentResponse)
def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db)
):
    """
    Assign an asset to a user
    """

    # Check if asset exists
    asset = db.query(Asset).filter(
        Asset.id == assignment.asset_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    # Check if user exists
    user = db.query(User).filter(
        User.id == assignment.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Create assignment
    new_assignment = AssetAssignment(
        asset_id=assignment.asset_id,
        user_id=assignment.user_id,
        assigned_date=assignment.assigned_date,
        notes=assignment.notes
    )

    # Update asset status
    asset.status = "assigned"

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return new_assignment

# GET ALL ASSIGNMENTS
@router.get("/assignments", response_model=list[AssignmentResponse])
def get_assignments(db: Session = Depends(get_db)):
    """
    Return all asset assignments
    """

    assignments = db.query(AssetAssignment).all()

    return assignments

@router.put("/assignments/{assignment_id}/return")
def return_asset(
    assignment_id: int,
    db: Session = Depends(get_db)
):
    """
    Return an assigned asset
    """

    assignment = db.query(AssetAssignment).filter(
        AssetAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Assignment not found"
        )

    # Prevent double return
    if assignment.returned_date:
        raise HTTPException(
            status_code=400,
            detail="Asset already returned"
        )

    # Set return date
    assignment.returned_date = date.today()

    # Update asset status
    asset = db.query(Asset).filter(
        Asset.id == assignment.asset_id
    ).first()

    if asset:
        asset.status = "available"

    db.commit()

    return {
        "message": "Asset returned successfully",
        "assignment_id": assignment.id,
        "returned_date": assignment.returned_date
    }

@router.get("/dashboard")
def dashboard_stats(db: Session = Depends(get_db)):
    """
    Dashboard statistics
    """

    total_assets = db.query(Asset).count()

    assigned_assets = db.query(Asset).filter(
        Asset.status == "assigned"
    ).count()

    available_assets = db.query(Asset).filter(
        Asset.status == "available"
    ).count()

    total_users = db.query(User).count()

    total_assignments = db.query(AssetAssignment).count()

    return {
        "total_assets": total_assets,
        "assigned_assets": assigned_assets,
        "available_assets": available_assets,
        "total_users": total_users,
        "total_assignments": total_assignments
    }

# GET SINGLE ASSET
@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    Get one asset by ID
    """

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    # If not found, return error
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset



# UPDATE ASSET

@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(asset_id: int, updated_data: AssetCreate, db: Session = Depends(get_db)):
    """
    Update existing asset
    """

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    # Update fields one by one
    for key, value in updated_data.dict().items():
        setattr(asset, key, value)

    db.commit()
    db.refresh(asset)

    return asset



# DELETE ASSET
@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    Delete asset from database
    """

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    db.delete(asset)
    db.commit()

    return {"message": "Asset deleted successfully"}
