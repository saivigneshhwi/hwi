from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv
import os

from routes import sos_routes, shelter_routes, auth_routes, dashboard_routes, hospital_routes
from database import engine, Base

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

@app.get("/")
async def root():
    return {"message": "Disaster Response Dashboard API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "disaster-response-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
