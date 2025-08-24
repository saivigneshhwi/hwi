#!/usr/bin/env python3
"""
Database initialization script for Disaster Response Dashboard
Creates sample data for testing and development
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from database import User, Organization, Division, Staff, Shelter, Hospital, ResourceCenter, SOSRequest
# Removed geoalchemy2 import for SQLite compatibility
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_sample_data():
    """Create sample data for the disaster response dashboard"""
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Creating sample organizations...")
        
        # Create sample organizations
        organizations = [
            Organization(
                name="Maharashtra Disaster Management Authority",
                type="Government",
                category="Emergency Response",
                address="Mantralaya, Mumbai, Maharashtra",
                contact_person="Dr. Rajesh Kumar",
                contact_phone="+91-22-12345678",
                contact_email="mdma@maharashtra.gov.in",
                capacity=1000,
                current_load=0
            ),
            Organization(
                name="Red Cross Society - Maharashtra",
                type="NGO",
                category="Relief",
                address="Red Cross Bhavan, Mumbai, Maharashtra",
                contact_person="Mrs. Priya Sharma",
                contact_phone="+91-22-87654321",
                contact_email="maharashtra@redcross.org",
                capacity=500,
                current_load=0
            ),
            Organization(
                name="Doctors Without Borders - India",
                type="NGO",
                category="Medical",
                address="Medical Center, Pune, Maharashtra",
                contact_person="Dr. Amit Patel",
                contact_phone="+91-20-98765432",
                contact_email="pune@msf.org",
                capacity=300,
                current_load=0
            ),
            Organization(
                name="Maharashtra Police Emergency Response",
                type="Government",
                category="Emergency Response",
                address="Police Headquarters, Mumbai, Maharashtra",
                contact_person="ACP Sanjay Deshmukh",
                contact_phone="+91-22-11223344",
                contact_email="emergency@maharashtrapolice.gov.in",
                capacity=800,
                current_load=0
            ),
            Organization(
                name="Volunteer Rescue Team",
                type="Volunteer Group",
                category="Rescue",
                address="Community Center, Nagpur, Maharashtra",
                contact_person="Mr. Ramesh Verma",
                contact_phone="+91-712-55667788",
                contact_email="rescue@volunteer.org",
                capacity=200,
                current_load=0
            )
        ]
        
        for org in organizations:
            db.add(org)
            db.commit()
        print(f"Created {len(organizations)} organizations")
        
        print("Creating sample divisions...")
        
        # Create sample divisions
        divisions = [
            Division(
                name="Emergency Medical Division",
                organization_id=organizations[0].id,  # MDMA
                type="Medical",
                description="Handles medical emergencies and health-related disasters",
                capacity=200,
                current_load=0
            ),
            Division(
                name="Search and Rescue Division",
                organization_id=organizations[0].id,  # MDMA
                type="Rescue",
                description="Specialized in search and rescue operations",
                capacity=150,
                current_load=0
            ),
            Division(
                name="Logistics and Supply Division",
                organization_id=organizations[0].id,  # MDMA
                type="Logistics",
                description="Manages supply chains and resource distribution",
                capacity=100,
                current_load=0
            ),
            Division(
                name="Medical Relief Division",
                organization_id=organizations[1].id,  # Red Cross
                type="Medical",
                description="Provides medical relief and first aid",
                capacity=100,
                current_load=0
            ),
            Division(
                name="Emergency Response Division",
                organization_id=organizations[3].id,  # Police
                type="Emergency Response",
                description="Handles law enforcement during disasters",
                capacity=200,
                current_load=0
            )
        ]
        
        for div in divisions:
            db.add(div)
        db.commit()
        print(f"Created {len(divisions)} divisions")
        
        print("Creating sample staff...")
        
        # Create sample staff members
        staff_members = [
            Staff(
                name="Dr. Rajesh Kumar",
                organization_id=organizations[0].id,  # MDMA
                division_id=divisions[0].id,  # Emergency Medical
                role="Manager",
                skills="Emergency Medicine, Disaster Management, Team Leadership",
                contact_phone="+91-22-12345678",
                contact_email="rajesh.kumar@mdma.gov.in",
                current_location="Mumbai",
                availability="Available"
            ),
            Staff(
                name="Capt. Priya Sharma",
                organization_id=organizations[0].id,  # MDMA
                division_id=divisions[1].id,  # Search and Rescue
                role="Specialist",
                skills="Search and Rescue, Mountaineering, Emergency Response",
                contact_phone="+91-22-12345679",
                contact_email="priya.sharma@mdma.gov.in",
                current_location="Mumbai",
                availability="Available"
            ),
            Staff(
                name="Mr. Amit Patel",
                organization_id=organizations[0].id,  # MDMA
                division_id=divisions[2].id,  # Logistics
                role="Worker",
                skills="Supply Chain Management, Inventory Control, Transportation",
                contact_phone="+91-22-12345680",
                contact_email="amit.patel@mdma.gov.in",
                current_location="Mumbai",
                availability="Available"
            ),
            Staff(
                name="Dr. Meera Desai",
                organization_id=organizations[1].id,  # Red Cross
                division_id=divisions[3].id,  # Medical Relief
                role="Specialist",
                skills="Emergency Medicine, First Aid, Trauma Care",
                contact_phone="+91-22-87654321",
                contact_email="meera.desai@redcross.org",
                current_location="Mumbai",
                availability="Available"
            ),
            Staff(
                name="ACP Sanjay Deshmukh",
                organization_id=organizations[3].id,  # Police
                division_id=divisions[4].id,  # Emergency Response
                role="Manager",
                skills="Law Enforcement, Crisis Management, Public Safety",
                contact_phone="+91-22-11223344",
                contact_email="sanjay.deshmukh@maharashtrapolice.gov.in",
                current_location="Mumbai",
                availability="Available"
            )
        ]
        
        for staff in staff_members:
            db.add(staff)
        db.commit()
        print(f"Created {len(staff_members)} staff members")
        
        print("Creating sample users...")
        
        # Create sample users
        users = [
            User(
                username="admin",
                email="admin@disaster-response.gov.in",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                organization_id=organizations[0].id,  # MDMA
                division_id=divisions[0].id  # Emergency Medical
            ),
            User(
                username="responder",
                email="responder@disaster-response.gov.in",
                hashed_password=get_password_hash("responder123"),
                role="responder",
                organization_id=organizations[0].id,  # MDMA
                division_id=divisions[1].id  # Search and Rescue
            ),
            User(
                username="viewer",
                email="viewer@disaster-response.gov.in",
                hashed_password=get_password_hash("viewer123"),
                role="viewer",
                organization_id=organizations[1].id,  # Red Cross
                division_id=divisions[3].id  # Medical Relief
            )
        ]
        
        for user in users:
            db.add(user)
        db.commit()
        print(f"Created {len(users)} users")
        
        print("Creating sample shelters...")
        
        # Create sample shelters
        shelters = [
            Shelter(
                name="Emergency Shelter - Mumbai Central",
                organization_id=organizations[0].id,  # MDMA
                longitude=72.8750,
                latitude=19.0760,
                address="Mumbai Central Station, Mumbai, Maharashtra",
                capacity=500,
                current_occupancy=120,
                type="Emergency",
                status="Active",
                contact_person="Rajesh Kumar",
                contact_phone="+91-22-12345678",
                facilities="Beds, Food, Water, Medical Aid, Sanitation"
            ),
            Shelter(
                name="Temporary Shelter - Pune",
                organization_id=organizations[1].id,  # Red Cross
                longitude=73.8563,
                latitude=18.5204,
                address="Pune Municipal Corporation, Pune, Maharashtra",
                capacity=300,
                current_occupancy=85,
                type="Temporary",
                status="Active",
                contact_person="Priya Sharma",
                contact_phone="+91-20-87654321",
                facilities="Beds, Food, Water, Basic Medical Care"
            ),
            Shelter(
                name="Relief Camp - Nagpur",
                organization_id=organizations[4].id,  # Volunteer Team
                longitude=79.0882,
                latitude=21.1458,
                address="Nagpur District Office, Nagpur, Maharashtra",
                capacity=400,
                current_occupancy=200,
                type="Relief",
                status="Active",
                contact_person="Amit Patel",
                contact_phone="+91-712-98765432",
                facilities="Beds, Food, Water, Clothing, Medical Aid"
            )
        ]
        
        for shelter in shelters:
            db.add(shelter)
        db.commit()
        print(f"Created {len(shelters)} shelters")
        
        print("Creating sample hospitals...")
        
        # Create sample hospitals
        hospitals = [
            Hospital(
                name="JJ Hospital Mumbai",
                organization_id=organizations[0].id,  # MDMA
                longitude=72.8750,
                latitude=19.0760,
                address="JJ Hospital, Byculla, Mumbai, Maharashtra",
                total_beds=1500,
                available_beds=450,
                icu_beds=100,
                available_icu=25,
                contact_phone="+91-22-12345678",
                specialties="Emergency Medicine, Trauma Care, Surgery, Pediatrics",
                emergency_services="24/7 Emergency, Trauma Center, Ambulance Service, ICU"
            ),
            Hospital(
                name="Sassoon General Hospital",
                organization_id=organizations[2].id,  # Doctors Without Borders
                longitude=73.8563,
                latitude=18.5204,
                address="Sassoon Road, Pune, Maharashtra",
                total_beds=800,
                available_beds=180,
                icu_beds=60,
                available_icu=15,
                contact_phone="+91-20-87654321",
                specialties="General Medicine, Surgery, Emergency Care",
                emergency_services="Emergency Department, Ambulance, Basic ICU"
            ),
            Hospital(
                name="Government Medical College Nagpur",
                organization_id=organizations[0].id,  # MDMA
                longitude=79.0882,
                latitude=21.1458,
                address="GMCH Campus, Nagpur, Maharashtra",
                total_beds=600,
                available_beds=120,
                icu_beds=40,
                available_icu=8,
                contact_phone="+91-712-98765432",
                specialties="General Medicine, Surgery, Emergency Medicine",
                emergency_services="Emergency Ward, Trauma Care, Ambulance"
            )
        ]
        
        for hospital in hospitals:
            db.add(hospital)
        db.commit()
        print(f"Created {len(hospitals)} hospitals")
        
        print("Creating sample resource centers...")
        
        # Create sample resource centers
        resource_centers = [
            ResourceCenter(
                name="Food Distribution Center - Mumbai",
                organization_id=organizations[0].id,  # MDMA
                longitude=72.8750,
                latitude=19.0760,
                address="Mumbai Central, Mumbai, Maharashtra",
                type="Food",
                inventory="Rice, Dal, Cooking Oil, Vegetables, Bread, Milk",
                contact_person="Suresh Iyer",
                contact_phone="+91-22-12345678",
                capacity=1000,
                current_stock=750
            ),
            ResourceCenter(
                name="Medical Supply Depot - Pune",
                organization_id=organizations[2].id,  # Doctors Without Borders
                longitude=73.8563,
                latitude=18.5204,
                address="Pune Medical College, Pune, Maharashtra",
                type="Medicine",
                inventory="Paracetamol, Antibiotics, Bandages, First Aid Kits, Oxygen Cylinders",
                contact_person="Dr. Meera Desai",
                contact_phone="+91-20-87654321",
                capacity=500,
                current_stock=300
            ),
            ResourceCenter(
                name="Clothing Distribution - Nagpur",
                organization_id=organizations[4].id,  # Volunteer Team
                longitude=79.0882,
                latitude=21.1458,
                address="Nagpur District Office, Nagpur, Maharashtra",
                type="Clothing",
                inventory="Blankets, Warm Clothes, Sarees, Shirts, Pants, Children's Clothes",
                contact_person="Lakshmi Devi",
                contact_phone="+91-712-98765432",
                capacity=800,
                current_stock=600
            )
        ]
        
        for center in resource_centers:
            db.add(center)
        db.commit()
        print(f"Created {len(resource_centers)} resource centers")
        
        print("Creating sample SOS request...")
        
        # Create a single sample SOS request
        from datetime import datetime, timedelta
        
        sample_sos = SOSRequest(
            external_id="SOS-001",
            status="Pending",
            people=15,
            longitude=72.8750,
            latitude=19.0760,
            text="Heavy monsoon rains causing severe flooding in coastal villages. Multiple families stranded, need immediate rescue and evacuation.",
            place="Konkan Coast, Maharashtra",
            timestamp=datetime.utcnow(),
            category="Needs Rescue",
            priority=5,
            assigned_to=staff_members[1].id,  # Rescue Specialist
            assigned_organization=organizations[0].id,  # MDMA
            assigned_division=divisions[1].id,  # Search and Rescue
            notes="Emergency flood response needed in coastal region",
            estimated_completion=None,
            actual_completion=None,
            assignment_time=datetime.utcnow(),
            accepted_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(sample_sos)
        db.commit()
        print("Created 1 sample SOS request")
        
        print("\n✅ Database initialization completed successfully!")
        print("\nSample data created:")
        print(f"- Organizations: {len(organizations)}")
        print(f"- Divisions: {len(divisions)}")
        print(f"- Staff Members: {len(staff_members)}")
        print(f"- Users: {len(users)}")
        print(f"- Shelters: {len(shelters)}")
        print(f"- Hospitals: {len(hospitals)}")
        print(f"- Resource Centers: {len(resource_centers)}")
        print(f"- SOS Requests: 1")
        print("\nDefault login credentials:")
        print("- Admin: admin / admin123")
        print("- Responder: responder / responder123")
        print("- Viewer: viewer / viewer123")
        print("\nSample SOS request created for testing the system!")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing Disaster Response Dashboard Database...")
    create_sample_data()
