
# Pydantic is used for data validation
from pydantic import BaseModel
from datetime import date, datetime
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

class UserUpdate(BaseModel):
    username: str
    email: str
    department: str | None = None
    role: str = "employee"

# ASSIGNMENT SCHEMAS

class AssignmentBase(BaseModel):
    """
    Shared fields for asset assignments
    """

    asset_id: int
    user_id: int
    assigned_date: date
    notes: Optional[str] = None



class AssignmentCreate(AssignmentBase):
    """
    Used when assigning an asset to a user
    """
    pass


class AssignmentResponse(AssignmentBase):
    """
    Returned by the API
    Includes database-generated fields
    """

    id: int
    returned_date: Optional[date] = None

    class Config:
        from_attributes = True

class AssignmentResponse(BaseModel):
    id: int
    asset_id: int
    user_id: int
    assigned_date: date
    returned_date: date | None = None
    notes: str | None = None

    class Config:
        from_attributes = True

class MaintenanceBase(BaseModel):
    asset_id: int
    issue_description: str
    issue_date: date

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceResponse(MaintenanceBase):
    id: int
    repair_description: str | None = None
    repair_date: date | None = None
    repair_cost: float | None = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class MaintenanceUpdate(BaseModel):
    repair_description: str | None = None
    repair_date: date | None = None
    repair_cost: float | None = None
    status: str

    class Config:
        from_attributes = True