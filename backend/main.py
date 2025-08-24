import os

import uvicorn
from database import Base, engine
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import routes
from routes import auth_routes
from routes import dashboard_routes
from routes import hospital_routes
from routes import shelter_routes
from routes import sos_routes
from routes import organization_routes
from routes import staff_routes
from routes import division_routes
from routes import emergency_routes
from routes import flood_detection_routes

# Load environment variables (optional)
try:
    load_dotenv()
except:
    pass

# Try to create database tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not create database tables: {e}")
    print("   The API will start but database operations will fail")

app = FastAPI(
    title="Disaster Response Dashboard API",
    description="API for managing disaster response operations in Maharashtra",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routes
app.include_router(sos_routes.router, prefix="/api/sos", tags=["SOS"])
app.include_router(shelter_routes.router, prefix="/api/shelters", tags=["Shelters"])
app.include_router(hospital_routes.router, prefix="/api/hospitals", tags=["Hospitals"])
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(organization_routes.router, prefix="/api/organizations", tags=["Organizations"])
app.include_router(staff_routes.router, prefix="/api/staff", tags=["Staff"])
app.include_router(division_routes.router, prefix="/api/divisions", tags=["Divisions"])
app.include_router(emergency_routes.router, prefix="/api/emergency", tags=["Emergency Response"])
app.include_router(flood_detection_routes.router, prefix="/api/flood-detection", tags=["Flood Detection"])

@app.get("/")
async def root():
    return {"message": "Disaster Response Dashboard API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "disaster-response-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
