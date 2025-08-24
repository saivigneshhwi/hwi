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
from database import User, SOSRequest, Shelter, Hospital, ResourceCenter
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
        print("Creating sample users...")
        
        # Create sample users
        users = [
            User(
                username="admin",
                email="admin@disaster-response.gov.in",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                organization="Maharashtra Disaster Management Authority"
            ),
            User(
                username="responder",
                email="responder@disaster-response.gov.in",
                hashed_password=get_password_hash("responder123"),
                role="responder",
                organization="Emergency Response Team"
            ),
            User(
                username="viewer",
                email="viewer@disaster-response.gov.in",
                hashed_password=get_password_hash("viewer123"),
                role="viewer",
                organization="Public Information Office"
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
                longitude=72.8750,
                latitude=19.0760,
                address="Mumbai Central Station, Mumbai, Maharashtra",
                capacity=500,
                current_occupancy=120,
                type="Emergency",
                status="Active",
                contact_person="Rajesh Kumar",
                contact_phone="+91-22-12345678"
            ),
            Shelter(
                name="Temporary Shelter - Pune",
                longitude=73.8563,
                latitude=18.5204,
                address="Pune Municipal Corporation, Pune, Maharashtra",
                capacity=300,
                current_occupancy=85,
                type="Temporary",
                status="Active",
                contact_person="Priya Sharma",
                contact_phone="+91-20-87654321"
            ),
            Shelter(
                name="Relief Camp - Nagpur",
                longitude=79.0882,
                latitude=21.1458,
                address="Nagpur District Office, Nagpur, Maharashtra",
                capacity=400,
                current_occupancy=200,
                type="Relief",
                status="Active",
                contact_person="Amit Patel",
                contact_phone="+91-712-98765432"
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
                longitude=72.8750,
                latitude=19.0760,
                address="JJ Hospital, Byculla, Mumbai, Maharashtra",
                total_beds=1500,
                available_beds=450,
                icu_beds=100,
                available_icu=25,
                contact_phone="+91-22-12345678"
            ),
            Hospital(
                name="Sassoon General Hospital",
                longitude=73.8563,
                latitude=18.5204,
                address="Sassoon Road, Pune, Maharashtra",
                total_beds=800,
                available_beds=180,
                icu_beds=60,
                available_icu=15,
                contact_phone="+91-20-87654321"
            ),
            Hospital(
                name="Government Medical College Nagpur",
                longitude=79.0882,
                latitude=21.1458,
                address="GMCH Campus, Nagpur, Maharashtra",
                total_beds=600,
                available_beds=120,
                icu_beds=40,
                available_icu=8,
                contact_phone="+91-712-98765432"
            )
        ]
        
        for hospital in hospitals:
            db.add(hospital)
        db.commit()
        print(f"Created {len(hospitals)} hospitals")
        
        print("Creating sample SOS requests...")
        
        # Create sample SOS requests
        sos_requests = [
            SOSRequest(
                external_id="1755968763493",
                status="Pending",
                people=1,
                longitude=77.301,
                latitude=30.139,
                text="Still no electricity since yesterday. Water supply is erratic. Please send any available relief kits for our area. We are running out of essentials.",
                place="Surat, Gujarat",
                category="Needs Rescue",
                priority=5,
                timestamp=datetime.utcnow() - timedelta(hours=2)
            ),
            SOSRequest(
                external_id="1755968763494",
                status="In Progress",
                people=5,
                longitude=72.8750,
                latitude=19.0760,
                text="Family of 5 needs immediate medical attention. Elderly member showing COVID symptoms. Need ambulance and medical supplies.",
                place="Mumbai Central, Maharashtra",
                category="Medical Emergency",
                priority=4,
                timestamp=datetime.utcnow() - timedelta(hours=1)
            ),
            SOSRequest(
                external_id="1755968763495",
                status="Done",
                people=12,
                longitude=73.8563,
                latitude=18.5204,
                text="Flood affected area. 12 people including 3 children need immediate evacuation. Water level rising rapidly.",
                place="Pune, Maharashtra",
                category="Needs Rescue",
                priority=5,
                timestamp=datetime.utcnow() - timedelta(hours=6)
            ),
            SOSRequest(
                external_id="1755968763496",
                status="Pending",
                people=8,
                longitude=79.0882,
                latitude=21.1458,
                text="Food shortage in relief camp. 8 people haven't received meals for 24 hours. Need immediate food supplies.",
                place="Nagpur, Maharashtra",
                category="Food",
                priority=3,
                timestamp=datetime.utcnow() - timedelta(hours=3)
            ),
            SOSRequest(
                external_id="1755968763497",
                status="In Progress",
                people=3,
                longitude=72.8750,
                latitude=19.0760,
                text="Fire outbreak in residential building. 3 people trapped on 3rd floor. Need fire brigade immediately.",
                place="Mumbai, Maharashtra",
                category="Fire Emergency",
                priority=5,
                timestamp=datetime.utcnow() - timedelta(minutes=30)
            )
        ]
        
        for sos in sos_requests:
            db.add(sos)
        db.commit()
        print(f"Created {len(sos_requests)} SOS requests")
        
        print("Creating sample resource centers...")
        
        # Create sample resource centers
        resource_centers = [
            ResourceCenter(
                name="Food Distribution Center - Mumbai",
                longitude=72.8750,
                latitude=19.0760,

                address="Mumbai Central, Mumbai, Maharashtra",
                type="Food",
                inventory="Rice, Dal, Cooking Oil, Vegetables, Bread, Milk",
                contact_person="Suresh Iyer",
                contact_phone="+91-22-12345678"
            ),
            ResourceCenter(
                name="Medical Supply Depot - Pune",
                longitude=73.8563,
                latitude=18.5204,

                address="Pune Medical College, Pune, Maharashtra",
                type="Medicine",
                inventory="Paracetamol, Antibiotics, Bandages, First Aid Kits, Oxygen Cylinders",
                contact_person="Dr. Meera Desai",
                contact_phone="+91-20-87654321"
            ),
            ResourceCenter(
                name="Clothing Distribution - Nagpur",
                longitude=79.0882,
                latitude=21.1458,

                address="Nagpur District Office, Nagpur, Maharashtra",
                type="Clothing",
                inventory="Blankets, Warm Clothes, Sarees, Shirts, Pants, Children's Clothes",
                contact_person="Lakshmi Devi",
                contact_phone="+91-712-98765432"
            )
        ]
        
        for center in resource_centers:
            db.add(center)
        db.commit()
        print(f"Created {len(resource_centers)} resource centers")
        
        print("\n✅ Database initialization completed successfully!")
        print("\nSample data created:")
        print(f"- Users: {len(users)}")
        print(f"- Shelters: {len(shelters)}")
        print(f"- Hospitals: {len(hospitals)}")
        print(f"- SOS Requests: {len(sos_requests)}")
        print(f"- Resource Centers: {len(resource_centers)}")
        print("\nDefault login credentials:")
        print("- Admin: admin / admin123")
        print("- Responder: responder / responder123")
        print("- Viewer: viewer / viewer123")
        
    except Exception as e:
        print(f"❌ Error during database initialization: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing Disaster Response Dashboard Database...")
    create_sample_data()
