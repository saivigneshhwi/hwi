from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# SOS Request Models
class SOSRequestBase(BaseModel):
    people: int = Field(..., ge=1, description="Number of people affected")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    text: str = Field(..., description="Description of the emergency")
    place: str = Field(..., description="Location name")
    category: str = Field(..., description="Type of emergency")

class SOSRequestCreate(SOSRequestBase):
    external_id: str = Field(..., description="External ID from n8n")

class SOSRequestUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class SOSRequestResponse(SOSRequestBase):
    id: UUID
    external_id: str
    status: str
    priority: int
    assigned_to: Optional[str]
    notes: Optional[str]
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Shelter Models
class ShelterBase(BaseModel):
    name: str
    longitude: float
    latitude: float
    address: str
    capacity: int
    type: str
    contact_person: str
    contact_phone: str

class ShelterCreate(ShelterBase):
    pass

class ShelterUpdate(BaseModel):
    current_occupancy: Optional[int] = None
    status: Optional[str] = None

class ShelterResponse(ShelterBase):
    id: UUID
    current_occupancy: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Hospital Models
class HospitalBase(BaseModel):
    name: str
    longitude: float
    latitude: float
    address: str
    total_beds: int
    icu_beds: int
    contact_phone: str

class HospitalCreate(HospitalBase):
    pass

class HospitalUpdate(BaseModel):
    available_beds: Optional[int] = None
    available_icu: Optional[int] = None

class HospitalResponse(HospitalBase):
    id: UUID
    available_beds: int
    available_icu: int
    created_at: datetime

    class Config:
        from_attributes = True

# Resource Center Models
class ResourceCenterBase(BaseModel):
    name: str
    longitude: float
    latitude: float
    address: str
    type: str
    inventory: str
    contact_person: str
    contact_phone: str

class ResourceCenterCreate(ResourceCenterBase):
    pass

class ResourceCenterResponse(ResourceCenterBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Models
class DashboardStats(BaseModel):
    total_sos: int
    pending_sos: int
    in_progress_sos: int
    completed_sos: int
    total_people_affected: int
    total_shelter_capacity: int
    available_shelter_capacity: int
    total_hospital_beds: int
    available_hospital_beds: int

class RegionStats(BaseModel):
    region: str
    sos_count: int
    people_affected: int
    shelter_capacity: int
    shelter_available: int

# Authentication Models
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"
    organization: Optional[str] = None

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    organization: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Map and Location Models
class Location(BaseModel):
    longitude: float
    latitude: float
    address: str

class MapBounds(BaseModel):
    north: float
    south: float
    east: float
    west: float

class SOSMapData(BaseModel):
    id: UUID
    longitude: float
    latitude: float
    status: str
    category: str
    priority: int
    people: int
    place: str

    class Config:
        from_attributes = True
