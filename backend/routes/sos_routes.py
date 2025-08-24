from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
# Removed geoalchemy2 imports for SQLite compatibility

from database import get_db, SOSRequest
from models import SOSRequestCreate, SOSRequestUpdate, SOSRequestResponse, SOSMapData
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=SOSRequestResponse)
async def create_sos_request(
    sos_data: SOSRequestCreate,
    db: Session = Depends(get_db)
):
    """Create a new SOS request from n8n workflow"""
    try:
        # Determine priority based on category and people affected
        priority = 1
        if sos_data.category.lower() in ["needs rescue", "medical emergency", "fire"]:
            priority = 5
        elif sos_data.category.lower() in ["food", "water", "shelter"]:
            priority = 3
        elif sos_data.people > 10:
            priority = 4
        
        db_sos = SOSRequest(
            external_id=sos_data.external_id,
            people=sos_data.people,
            longitude=sos_data.longitude,
            latitude=sos_data.latitude,
            text=sos_data.text,
            place=sos_data.place,
            category=sos_data.category.strip(),
            priority=priority,
            timestamp=datetime.utcnow()
        )
        
        db.add(db_sos)
        db.commit()
        db.refresh(db_sos)
        
        return db_sos
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating SOS request: {str(e)}")

@router.get("/", response_model=List[SOSRequestResponse])
async def get_sos_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    region: Optional[str] = Query(None, description="Filter by region (Western, Central, Vidarbha)"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority"),
    limit: int = Query(100, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get SOS requests with filtering options"""
    query = db.query(SOSRequest)
    
    if status:
        query = query.filter(SOSRequest.status == status)
    if category:
        query = query.filter(SOSRequest.category.ilike(f"%{category}%"))
    if priority:
        query = query.filter(SOSRequest.priority == priority)
    
    # Region filtering based on coordinates
    if region:
        if region.lower() == "western":
            query = query.filter(SOSRequest.longitude >= 72.0, SOSRequest.longitude <= 75.0)
        elif region.lower() == "central":
            query = query.filter(SOSRequest.longitude >= 75.0, SOSRequest.longitude <= 78.0)
        elif region.lower() == "vidarbha":
            query = query.filter(SOSRequest.longitude >= 78.0, SOSRequest.longitude <= 81.0)
    
    query = query.order_by(SOSRequest.priority.desc(), SOSRequest.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    return query.all()

@router.get("/map", response_model=List[SOSMapData])
async def get_sos_map_data(
    bounds: Optional[str] = Query(None, description="Map bounds: north,south,east,west"),
    db: Session = Depends(get_db)
):
    """Get SOS data for map visualization"""
    query = db.query(SOSRequest).filter(SOSRequest.status != "Done")
    
    if bounds:
        try:
            north, south, east, west = map(float, bounds.split(','))
            # Filter by bounding box
            query = query.filter(
                SOSRequest.latitude <= north,
                SOSRequest.latitude >= south,
                SOSRequest.longitude <= east,
                SOSRequest.longitude >= west
            )
        except ValueError:
            pass
    
    return query.all()

@router.get("/{sos_id}", response_model=SOSRequestResponse)
async def get_sos_request(sos_id: str, db: Session = Depends(get_db)):
    """Get a specific SOS request by ID"""
    try:
        sos_uuid = uuid.UUID(sos_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    sos = db.query(SOSRequest).filter(SOSRequest.id == sos_uuid).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    return sos

@router.put("/{sos_id}", response_model=SOSRequestResponse)
async def update_sos_request(
    sos_id: str,
    sos_update: SOSRequestUpdate,
    db: Session = Depends(get_db)
):
    """Update an SOS request status and details"""
    try:
        sos_uuid = uuid.UUID(sos_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    sos = db.query(SOSRequest).filter(SOSRequest.id == sos_uuid).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    update_data = sos_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sos, field, value)
    
    sos.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(sos)
    
    return sos

@router.delete("/{sos_id}")
async def delete_sos_request(sos_id: str, db: Session = Depends(get_db)):
    """Delete an SOS request (admin only)"""
    try:
        sos_uuid = uuid.UUID(sos_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    sos = db.query(SOSRequest).filter(SOSRequest.id == sos_uuid).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    db.delete(sos)
    db.commit()
    
    return {"message": "SOS request deleted successfully"}

@router.get("/stats/summary")
async def get_sos_summary(db: Session = Depends(get_db)):
    """Get summary statistics for SOS requests"""
    total = db.query(func.count(SOSRequest.id)).scalar()
    pending = db.query(func.count(SOSRequest.id)).filter(SOSRequest.status == "Pending").scalar()
    in_progress = db.query(func.count(SOSRequest.id)).filter(SOSRequest.status == "In Progress").scalar()
    completed = db.query(func.count(SOSRequest.id)).filter(SOSRequest.status == "Done").scalar()
    total_people = db.query(func.sum(SOSRequest.people)).scalar() or 0
    
    return {
        "total_requests": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "total_people_affected": total_people
    }

@router.get("/stats/by-category")
async def get_sos_by_category(db: Session = Depends(get_db)):
    """Get SOS requests grouped by category"""
    result = db.query(
        SOSRequest.category,
        func.count(SOSRequest.id).label('count'),
        func.sum(SOSRequest.people).label('people_affected')
    ).group_by(SOSRequest.category).all()
    
    return [
        {
            "category": item.category,
            "count": item.count,
            "people_affected": item.people_affected or 0
        }
        for item in result
    ]

@router.get("/stats/by-region")
async def get_sos_by_region(db: Session = Depends(get_db)):
    """Get SOS requests grouped by region"""
    regions = [
        ("Western Maharashtra", 72.0, 75.0),
        ("Central Maharashtra", 75.0, 78.0),
        ("Vidarbha", 78.0, 81.0)
    ]
    
    region_stats = []
    for region_name, west_lon, east_lon in regions:
        count = db.query(func.count(SOSRequest.id)).filter(
            SOSRequest.longitude >= west_lon,
            SOSRequest.longitude <= east_lon
        ).scalar()
        
        people = db.query(func.sum(SOSRequest.people)).filter(
            SOSRequest.longitude >= west_lon,
            SOSRequest.longitude <= east_lon
        ).scalar() or 0
        
        region_stats.append({
            "region": region_name,
            "sos_count": count,
            "people_affected": people
        })
    
    return region_stats
