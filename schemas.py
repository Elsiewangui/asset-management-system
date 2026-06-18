# schemas.py

# Pydantic is used for data validation
from pydantic import BaseModel
from datetime import date
from typing import Optional



# BASE SCHEMA (shared fields)
class AssetBase(BaseModel):
    """
    Shared fields for Asset
    Used by both Create and Response schemas
    """

    asset_tag: str
    device_type: str  # laptop, printer, monitor
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: str
    status: str = "available"
    purchase_date: Optional[date] = None



# CREATE SCHEMA(POST)
class AssetCreate(AssetBase):
    """
    Used when creating a new asset (POST)
    """
    pass



# RESPONSE SCHEMA(GET)
class AssetResponse(AssetBase):
    """
    Used when returning data from API
    Includes database-generated fields like ID
    """

    id: int

    class Config:
        from_attributes = True


# USER SCHEMAS
class UserBase(BaseModel):
    """
    Shared user fields
    """

    username: str
    email: str
    department: str | None = None
    role: str = "employee"


class UserCreate(UserBase):
    """
    Used when creating a user
    """
    password: str


class UserResponse(UserBase):
    """
    Returned to API users
    """

    id: int

    class Config:
        from_attributes = True