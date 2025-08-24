from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
import math
from datetime import datetime

from database import get_db, SOSRequest, Organization, Staff, Division, TicketUpdate
from models import SOSRequestCreate, SOSRequestUpdate, SOSRequestResponse, SOSMapData, TicketUpdateCreate
import uuid
from database import Shelter, Hospital

router = APIRouter()

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def find_nearest_organization(sos_lat, sos_lon, db: Session):
    """Find the nearest available organization for the SOS request"""
    organizations = db.query(Organization).filter(Organization.status == "Active").all()
    
    if not organizations:
        return None
    
    nearest_org = None
    min_distance = float('inf')
    
    for org in organizations:
        # For now, use Mumbai coordinates as default for organizations
        # In production, add lat/lon to Organization model
        org_lat, org_lon = 19.0760, 72.8750  # Mumbai coordinates
        
        distance = calculate_distance(sos_lat, sos_lon, org_lat, org_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_org = org
    
    return nearest_org

def find_nearest_staff(sos_lat, sos_lon, category, db: Session):
    """Find the nearest available staff member for the SOS request"""
    # Filter staff by category and availability
    if category.lower() in ["medical emergency", "medical"]:
        staff_query = db.query(Staff).filter(
            Staff.status == "Active",
            Staff.availability == "Available",
            Staff.skills.ilike("%medical%")
        )
    elif category.lower() in ["needs rescue", "fire emergency"]:
        staff_query = db.query(Staff).filter(
            Staff.status == "Active",
            Staff.availability == "Available",
            Staff.skills.ilike("%rescue%")
        )
    else:
        staff_query = db.query(Staff).filter(
            Staff.status == "Active",
            Staff.availability == "Available"
        )
    
    available_staff = staff_query.all()
    
    if not available_staff:
        return None
    
    nearest_staff = None
    min_distance = float('inf')
    
    for staff in available_staff:
        # For now, use Mumbai coordinates as default
        # In production, add current_location coordinates to Staff model
        staff_lat, staff_lon = 19.0760, 72.8750
        
        distance = calculate_distance(sos_lat, sos_lon, staff_lat, staff_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_staff = staff
    
    return nearest_staff

@router.post("/", response_model=SOSRequestResponse)
async def create_sos_request(
    sos_data: SOSRequestCreate,
    db: Session = Depends(get_db)
):
    """Create a new SOS request from n8n workflow with smart assignment"""
    try:
        # Determine priority based on category and people affected
        priority = 1
        if sos_data.category.lower() in ["needs rescue", "medical emergency", "fire"]:
            priority = 5
        elif sos_data.category.lower() in ["food", "water", "shelter"]:
            priority = 3
        elif sos_data.people > 10:
            priority = 4
        
        # Find nearest organization and staff
        nearest_org = find_nearest_organization(sos_data.latitude, sos_data.longitude, db)
        nearest_staff = find_nearest_staff(sos_data.latitude, sos_data.longitude, sos_data.category, db)
        
        db_sos = SOSRequest(
            external_id=sos_data.external_id,
            people=sos_data.people,
            longitude=sos_data.longitude,
            latitude=sos_data.latitude,
            text=sos_data.text,
            place=sos_data.place,
            category=sos_data.category.strip(),
            priority=priority,
            assigned_organization=nearest_org.id if nearest_org else None,
            assigned_to=nearest_staff.id if nearest_staff else None,
            timestamp=datetime.utcnow()
        )
        
        db.add(db_sos)
        db.commit()
        db.refresh(db_sos)
        
        # Create ticket update record
        if nearest_org or nearest_staff:
            update_record = TicketUpdate(
                ticket_id=str(db_sos.id),
                updated_by=nearest_staff.id if nearest_staff else "system",
                field_name="initial_assignment",
                new_value=f"Assigned to {nearest_org.name if nearest_org else 'No org'} - {nearest_staff.name if nearest_staff else 'No staff'}",
                notes="Automatic assignment based on location and availability"
            )
            db.add(update_record)
            db.commit()
        
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
    
    sos_requests = query.all()
    
    return [
        SOSMapData(
            id=str(sos.id),
            longitude=sos.longitude,
            latitude=sos.latitude,
            status=sos.status,
            category=sos.category,
            priority=sos.priority,
            people=sos.people,
            place=sos.place
        )
        for sos in sos_requests
    ]

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
    """Update an SOS request status and assignment"""
    # Try to find by string ID first, then by UUID
    sos = db.query(SOSRequest).filter(SOSRequest.id == sos_id).first()
    
    if not sos:
        try:
            sos_uuid = uuid.UUID(sos_id)
            sos = db.query(SOSRequest).filter(SOSRequest.id == sos_uuid).first()
        except ValueError:
            pass
    
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    # Store old values for update history
    old_status = sos.status
    old_assigned_to = sos.assigned_to
    old_notes = sos.notes
    
    # Update fields
    update_data = sos_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sos, field, value)
    
    sos.updated_at = datetime.utcnow()
    
    # Update completion time if status changed to Done
    if sos.status == "Done" and old_status != "Done":
        sos.actual_completion = datetime.utcnow()
    
    db.commit()
    db.refresh(sos)
    
    # Create update history records
    updates_to_record = []
    
    if sos.status != old_status:
        updates_to_record.append(TicketUpdate(
            ticket_id=str(sos.id),
            updated_by="system",  # In production, get from authenticated user
            field_name="status",
            old_value=old_status,
            new_value=sos.status,
            notes=sos_update.notes if hasattr(sos_update, 'notes') else None
        ))
    
    if sos.assigned_to != old_assigned_to:
        updates_to_record.append(TicketUpdate(
            ticket_id=str(sos.id),
            updated_by="system",
            field_name="assigned_to",
            old_value=old_assigned_to,
            new_value=sos.assigned_to,
            notes="Staff assignment updated"
        ))
    
    if sos.notes != old_notes:
        updates_to_record.append(TicketUpdate(
            ticket_id=str(sos.id),
            updated_by="system",
            field_name="notes",
            old_value=old_notes,
            new_value=sos.notes,
            notes="Notes updated"
        ))
    
    # Add update records to database
    for update_record in updates_to_record:
        db.add(update_record)
    
    if updates_to_record:
        db.commit()
    
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

@router.get("/{sos_id}/updates")
async def get_ticket_updates(sos_id: str, db: Session = Depends(get_db)):
    """Get update history for a specific SOS request"""
    try:
        sos_uuid = uuid.UUID(sos_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    updates = db.query(TicketUpdate).filter(TicketUpdate.ticket_id == str(sos_id)).order_by(TicketUpdate.update_time.desc()).all()
    return updates

@router.post("/{sos_id}/assign")
async def assign_sos_request(
    sos_id: str,
    assignment_data: dict,
    db: Session = Depends(get_db)
):
    """Manually assign an SOS request to organization/staff"""
    try:
        sos_uuid = uuid.UUID(sos_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    sos = db.query(SOSRequest).filter(SOSRequest.id == sos_uuid).first()
    if not sos:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    # Update assignment
    if 'organization_id' in assignment_data:
        sos.assigned_organization = assignment_data['organization_id']
    
    if 'staff_id' in assignment_data:
        sos.assigned_to = assignment_data['staff_id']
    
    if 'estimated_completion' in assignment_data:
        sos.estimated_completion = assignment_data['estimated_completion']
    
    sos.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(sos)
    
    # Create update record
    update_record = TicketUpdate(
        ticket_id=str(sos.id),
        updated_by="system",
        field_name="manual_assignment",
        new_value=f"Assigned to org: {assignment_data.get('organization_id', 'None')}, staff: {assignment_data.get('staff_id', 'None')}",
        notes="Manual assignment by operator"
    )
    db.add(update_record)
    db.commit()
    
    return sos

@router.get("/{sos_id}/nearest-facilities")
async def get_nearest_facilities(
    sos_id: str,
    db: Session = Depends(get_db)
):
    """Get nearest available shelter and hospital for an SOS request"""
    try:
        # Find the SOS request
        sos_request = None
        try:
            # Try to find by UUID first
            sos_request = db.query(SOSRequest).filter(SOSRequest.id == sos_id).first()
        except:
            # If UUID fails, try to find by string ID
            sos_request = db.query(SOSRequest).filter(SOSRequest.external_id == sos_id).first()
        
        if not sos_request:
            raise HTTPException(status_code=404, detail="SOS request not found")
        
        sos_lat = sos_request.latitude
        sos_lon = sos_request.longitude
        
        # Find nearest shelter with available capacity
        shelters = db.query(Shelter).filter(
            Shelter.status == "Active",
            Shelter.current_occupancy < Shelter.capacity
        ).all()
        
        nearest_shelter = None
        min_shelter_distance = float('inf')
        
        for shelter in shelters:
            distance = calculate_distance(sos_lat, sos_lon, shelter.latitude, shelter.longitude)
            if distance < min_shelter_distance:
                min_shelter_distance = distance
                nearest_shelter = {
                    "id": str(shelter.id),
                    "name": shelter.name,
                    "address": shelter.address,
                    "latitude": shelter.latitude,
                    "longitude": shelter.longitude,
                    "distance_km": round(distance, 2),
                    "available_capacity": shelter.capacity - shelter.current_occupancy,
                    "total_capacity": shelter.capacity,
                    "current_occupancy": shelter.current_occupancy,
                    "facilities": shelter.facilities,
                    "contact_person": shelter.contact_person,
                    "contact_phone": shelter.contact_phone,
                    "google_maps_url": f"https://www.google.com/maps/dir/{sos_lat},{sos_lon}/{shelter.latitude},{shelter.longitude}"
                }
        
        # Find nearest hospital with available beds
        hospitals = db.query(Hospital).filter(
            Hospital.available_beds > 0
        ).all()
        
        nearest_hospital = None
        min_hospital_distance = float('inf')
        
        for hospital in hospitals:
            distance = calculate_distance(sos_lat, sos_lon, hospital.latitude, hospital.longitude)
            if distance < min_hospital_distance:
                min_hospital_distance = distance
                nearest_hospital = {
                    "id": str(hospital.id),
                    "name": hospital.name,
                    "address": hospital.address,
                    "latitude": hospital.latitude,
                    "longitude": hospital.longitude,
                    "distance_km": round(distance, 2),
                    "available_beds": hospital.available_beds,
                    "total_beds": hospital.total_beds,
                    "available_icu": hospital.available_icu,
                    "total_icu": hospital.icu_beds,
                    "contact_phone": hospital.contact_phone,
                    "google_maps_url": f"https://www.google.com/maps/dir/{sos_lat},{sos_lon}/{hospital.latitude},{hospital.longitude}"
                }
        
        return {
            "sos_request": {
                "id": str(sos_request.id),
                "external_id": sos_request.external_id,
                "category": sos_request.category,
                "place": sos_request.place,
                "latitude": sos_request.latitude,
                "longitude": sos_request.longitude,
                "people": sos_request.people
            },
            "nearest_shelter": nearest_shelter,
            "nearest_hospital": nearest_hospital,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding nearest facilities: {str(e)}")
