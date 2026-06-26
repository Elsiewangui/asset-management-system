
# FastAPI tools for routing
from fastapi import APIRouter, Depends, HTTPException
from datetime import date

# SQLAlchemy session (to talk to database)
from sqlalchemy.orm import Session

# Import database session generator
from database import get_db

# Import your table model
from models import Asset,User, AssetAssignment, MaintenanceRecord
from schemas import AssetCreate, AssetResponse, UserResponse, UserCreate, AssignmentCreate, AssignmentResponse, UserUpdate, MaintenanceCreate, MaintenanceResponse,MaintenanceUpdate

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

    # Prevent double assignment
    if asset.status == "assigned":
        raise HTTPException(
            status_code=400,
            detail="Asset is already assigned"
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


# GET ASSIGNMENT HISTORY FOR AN ASSET
@router.get("/{asset_id}/history")
def get_asset_history(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Return assignment history for a specific asset
    """

    asset = db.query(Asset).filter(
        Asset.id == asset_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    assignments = db.query(AssetAssignment).filter(
        AssetAssignment.asset_id == asset_id
    ).all()

    return assignments

@router.get(
    "/{asset_id}/history",
    response_model=list[AssignmentResponse]
)
def get_asset_history(
    asset_id: int,
    db: Session = Depends(get_db)
):
    ...
@router.post(
    "/maintenance",
    response_model=MaintenanceResponse
)
def create_maintenance_record(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a maintenance record for an asset.
    """

    # Check if asset exists
    asset = db.query(Asset).filter(
        Asset.id == maintenance.asset_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Asset not found"
        )

    # Create maintenance record
    new_record = MaintenanceRecord(
        asset_id=maintenance.asset_id,
        issue_description=maintenance.issue_description,
        issue_date=maintenance.issue_date
    )

    # Update asset status
    asset.status = "under_repair"

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record

@router.get(
    "/maintenance",
    response_model=list[MaintenanceResponse]
)
def get_maintenance_records(
    db: Session = Depends(get_db)
):
    """
    Return all maintenance records.
    """

    records = db.query(MaintenanceRecord).all()

    return records

@router.put(
    "/maintenance/{record_id}",
    response_model=MaintenanceResponse
)
def update_maintenance_record(
    record_id: int,
    maintenance: MaintenanceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a maintenance record.
    """

    # Find maintenance record
    record = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.id == record_id
    ).first()

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found"
        )

    # Update fields
    record.repair_description = maintenance.repair_description
    record.repair_date = maintenance.repair_date
    record.repair_cost = maintenance.repair_cost
    record.status = maintenance.status

    # If repair completed, update asset status
    if maintenance.status == "completed":

        asset = db.query(Asset).filter(
            Asset.id == record.asset_id
        ).first()

        if asset:
            asset.status = "available"

    db.commit()
    db.refresh(record)

    return record

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

