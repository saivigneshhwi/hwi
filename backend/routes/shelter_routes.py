from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
# Removed geoalchemy2 import for SQLite compatibility

from database import get_db, Shelter
from models import ShelterCreate, ShelterUpdate, ShelterResponse
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=ShelterResponse)
async def create_shelter(
    shelter_data: ShelterCreate,
    db: Session = Depends(get_db)
):
    """Create a new shelter"""
    try:
        db_shelter = Shelter(
            name=shelter_data.name,
            longitude=shelter_data.longitude,
            latitude=shelter_data.latitude,
            address=shelter_data.address,
            capacity=shelter_data.capacity,
            type=shelter_data.type,
            contact_person=shelter_data.contact_person,
            contact_phone=shelter_data.contact_phone
        )
        
        db.add(db_shelter)
        db.commit()
        db.refresh(db_shelter)
        
        return db_shelter
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating shelter: {str(e)}")

@router.get("/", response_model=List[ShelterResponse])
async def get_shelters(
    type: Optional[str] = Query(None, description="Filter by shelter type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    region: Optional[str] = Query(None, description="Filter by region"),
    has_capacity: Optional[bool] = Query(None, description="Filter by availability"),
    db: Session = Depends(get_db)
):
    """Get shelters with filtering options"""
    query = db.query(Shelter)
    
    if type:
        query = query.filter(Shelter.type == type)
    if status:
        query = query.filter(Shelter.status == status)
    if has_capacity is not None:
        if has_capacity:
            query = query.filter(Shelter.current_occupancy < Shelter.capacity)
        else:
            query = query.filter(Shelter.current_occupancy >= Shelter.capacity)
    
    # Region filtering
    if region:
        if region.lower() == "western":
            query = query.filter(Shelter.longitude >= 72.0, Shelter.longitude <= 75.0)
        elif region.lower() == "central":
            query = query.filter(Shelter.longitude >= 75.0, Shelter.longitude <= 78.0)
        elif region.lower() == "vidarbha":
            query = query.filter(Shelter.longitude >= 78.0, Shelter.longitude <= 81.0)
    
    return query.all()

@router.get("/nearby")
async def get_nearby_shelters(
    latitude: float = Query(..., description="Current latitude"),
    longitude: float = Query(..., description="Current longitude"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    limit: int = Query(10, le=50, description="Maximum number of shelters to return"),
    db: Session = Depends(get_db)
):
    """Get shelters within a specified radius"""
    try:
        # Convert km to degrees (approximate)
        radius_degrees = radius_km / 111.0
        
        shelters = db.query(Shelter).filter(
            Shelter.longitude >= longitude - radius_degrees,
            Shelter.longitude <= longitude + radius_degrees,
            Shelter.latitude >= latitude - radius_degrees,
            Shelter.latitude <= latitude + radius_degrees
        ).limit(limit).all()
        
        # Calculate distances and sort
        shelter_distances = []
        for shelter in shelters:
            # Simple distance calculation (can be improved with PostGIS functions)
            lat_diff = abs(shelter.latitude - latitude)
            lon_diff = abs(shelter.longitude - longitude)
            distance = ((lat_diff ** 2 + lon_diff ** 2) ** 0.5) * 111.0  # Convert to km
            
            shelter_distances.append({
                "id": str(shelter.id),
                "name": shelter.name,
                "longitude": shelter.longitude,
                "latitude": shelter.latitude,
                "address": shelter.address,
                "capacity": shelter.capacity,
                "current_occupancy": shelter.current_occupancy,
                "available_capacity": shelter.capacity - shelter.current_occupancy,
                "type": shelter.type,
                "status": shelter.status,
                "contact_person": shelter.contact_person,
                "contact_phone": shelter.contact_phone,
                "distance_km": round(distance, 2)
            })
        
        # Sort by distance
        shelter_distances.sort(key=lambda x: x["distance_km"])
        
        return shelter_distances[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding nearby shelters: {str(e)}")

@router.get("/{shelter_id}", response_model=ShelterResponse)
async def get_shelter(shelter_id: str, db: Session = Depends(get_db)):
    """Get a specific shelter by ID"""
    try:
        shelter_uuid = uuid.UUID(shelter_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    shelter = db.query(Shelter).filter(Shelter.id == shelter_uuid).first()
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")
    
    return shelter

@router.put("/{shelter_id}", response_model=ShelterResponse)
async def update_shelter(
    shelter_id: str,
    shelter_update: ShelterUpdate,
    db: Session = Depends(get_db)
):
    """Update shelter information"""
    try:
        shelter_uuid = uuid.UUID(shelter_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    shelter = db.query(Shelter).filter(Shelter.id == shelter_uuid).first()
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")
    
    update_data = shelter_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shelter, field, value)
    
    # Update status based on occupancy
    if shelter.current_occupancy >= shelter.capacity:
        shelter.status = "Full"
    elif shelter.current_occupancy > 0:
        shelter.status = "Active"
    else:
        shelter.status = "Available"
    
    db.commit()
    db.refresh(shelter)
    
    return shelter

@router.delete("/{shelter_id}")
async def delete_shelter(shelter_id: str, db: Session = Depends(get_db)):
    """Delete a shelter (admin only)"""
    try:
        shelter_uuid = uuid.UUID(shelter_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    shelter = db.query(Shelter).filter(Shelter.id == shelter_uuid).first()
    if not shelter:
        raise HTTPException(status_code=404, detail="Shelter not found")
    
    db.delete(shelter)
    db.commit()
    
    return {"message": "Shelter deleted successfully"}

@router.get("/stats/overview")
async def get_shelter_overview(db: Session = Depends(get_db)):
    """Get shelter overview statistics"""
    try:
        total_shelters = db.query(func.count(Shelter.id)).scalar()
        total_capacity = db.query(func.sum(Shelter.capacity)).scalar() or 0
        current_occupancy = db.query(func.sum(Shelter.current_occupancy)).scalar() or 0
        available_capacity = total_capacity - current_occupancy
        
        # Status breakdown
        status_counts = db.query(
            Shelter.status,
            func.count(Shelter.id).label('count')
        ).group_by(Shelter.status).all()
        
        # Type breakdown
        type_counts = db.query(
            Shelter.type,
            func.count(Shelter.id).label('count'),
            func.sum(Shelter.capacity).label('total_capacity')
        ).group_by(Shelter.type).all()
        
        return {
            "total_shelters": total_shelters,
            "total_capacity": total_capacity,
            "current_occupancy": current_occupancy,
            "available_capacity": available_capacity,
            "utilization_rate": round(current_occupancy / total_capacity * 100, 2) if total_capacity > 0 else 0,
            "status_breakdown": [
                {
                    "status": item.status,
                    "count": item.count
                }
                for item in status_counts
            ],
            "type_breakdown": [
                {
                    "type": item.type,
                    "count": item.count,
                    "total_capacity": item.total_capacity or 0
                }
                for item in type_counts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching shelter overview: {str(e)}")
