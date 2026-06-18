
# FastAPI tools for routing
from fastapi import APIRouter, Depends, HTTPException

# SQLAlchemy session (to talk to database)
from sqlalchemy.orm import Session

# Import database session generator
from database import get_db

# Import your table model
from models import Asset,User
from schemas import AssetCreate, AssetResponse, UserResponse, UserCreate

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
