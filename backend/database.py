from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Load environment variables (optional)
try:
    load_dotenv()
except:
    pass

# Database connection - Using SQLite instead of PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./disaster_response.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SOS Request Model
class SOSRequest(Base):
    __tablename__ = "sos_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    external_id = Column(String, unique=True, index=True)  # n8n ID
    status = Column(String, default="Pending")  # Pending, In Progress, Done, Cancelled
    people = Column(Integer, default=1)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    text = Column(Text)
    place = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category = Column(String)  # Needs Rescue, Medical, Food, etc.
    priority = Column(Integer, default=1)  # 1-5, 5 being highest
    assigned_to = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Shelter Model
class Shelter(Base):
    __tablename__ = "shelters"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    address = Column(String)
    capacity = Column(Integer, default=0)
    current_occupancy = Column(Integer, default=0)
    type = Column(String)  # Emergency, Temporary, Permanent
    status = Column(String, default="Active")  # Active, Inactive, Full
    contact_person = Column(String)
    contact_phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Hospital Model
class Hospital(Base):
    __tablename__ = "hospitals"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    address = Column(String)
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)
    icu_beds = Column(Integer, default=0)
    available_icu = Column(Integer, default=0)
    contact_phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Resource Center Model
class ResourceCenter(Base):
    __tablename__ = "resource_centers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    address = Column(String)
    type = Column(String)  # Food, Medicine, Clothing, etc.
    inventory = Column(Text)  # JSON string of available items
    contact_person = Column(String)
    contact_phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# User Model for Authentication
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="viewer")  # admin, responder, viewer
    organization = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
