from fastapi import APIRouter, Query, HTTPException
import ee
import geemap
from datetime import datetime
from typing import Optional

router = APIRouter()

# Authenticate and initialize Earth Engine once
try:
    ee.Initialize(project='hwi2025')
except Exception as e:
    ee.Authenticate()
    ee.Initialize(project='hwi2025')

@router.get("/analyze")
async def analyze_flood_detection(
    latitude: float = Query(..., description="Latitude of the location to analyze"),
    longitude: float = Query(..., description="Longitude of the location to analyze"),
    radius_km: float = Query(10.0, description="Radius in kilometers around the point to analyze"),
    pre_flood_start: str = Query("2024-07-01", description="Pre-flood start date (YYYY-MM-DD)"),
    pre_flood_end: str = Query("2024-07-15", description="Pre-flood end date (YYYY-MM-DD)"),
    post_flood_start: str = Query("2024-07-16", description="Post-flood start date (YYYY-MM-DD)"),
    post_flood_end: str = Query("2024-07-31", description="Post-flood end date (YYYY-MM-DD)"),
    threshold: float = Query(1.5, description="Flood detection threshold (dB)")
):
    """
    Analyze flood detection for a specific location using Google Earth Engine
    """
    try:
        # Create a circular region around the specified coordinates
        point = ee.Geometry.Point([longitude, latitude])
        region = point.buffer(radius_km * 1000)  # Convert km to meters
        
        # Load Sentinel-1 VH data
        def get_s1_vh(start, end):
            return (ee.ImageCollection('COPERNICUS/S1_GRD')
                    .filterBounds(region)
                    .filterDate(start, end)
                    .filter(ee.Filter.eq('instrumentMode', 'IW'))
                    .filter(ee.Filter.eq('resolution_meters', 10))
                    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
                    .select('VH')
                    .mean())
        
        # Load Sentinel-1 VV data
        def get_s1_vv(start, end):
            return (ee.ImageCollection('COPERNICUS/S1_GRD')
                    .filterBounds(region)
                    .filterDate(start, end)
                    .filter(ee.Filter.eq('instrumentMode', 'IW'))
                    .filter(ee.Filter.eq('resolution_meters', 10))
                    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
                    .select('VV')
                    .mean())
        
        # Get pre and post flood images for both VH and VV
        pre_flood_vh = get_s1_vh(pre_flood_start, pre_flood_end)
        post_flood_vh = get_s1_vh(post_flood_start, post_flood_end)
        pre_flood_vv = get_s1_vv(pre_flood_start, pre_flood_end)
        post_flood_vv = get_s1_vv(post_flood_start, post_flood_end)
        
        # Calculate change detection for both polarizations
        vh_change = post_flood_vh.subtract(pre_flood_vh)
        vv_change = post_flood_vv.subtract(pre_flood_vv)
        
        # Apply permanent water mask using JRC dataset
        permanent_water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select('occurrence').gt(90)
        
        # Create flood detection masks
        vh_flooded = vh_change.lt(-threshold).selfMask()
        vv_flooded = vv_change.lt(-threshold).selfMask()
        
        # Combine both polarizations for final flood map
        flooded_areas = vh_flooded.Or(vv_flooded).updateMask(permanent_water.Not())
        
        # Calculate statistics
        flood_area = flooded_areas.multiply(ee.Image.pixelArea()).reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=region,
            scale=10,
            maxPixels=1e9
        ).get('VH')
        
        # Generate tile URLs for visualization
        def get_tile_url(image, vis_params):
            map_id_dict = ee.Image(image).getMapId(vis_params)
            return map_id_dict['tile_fetcher'].url_format
        
        # Visualization parameters
        pre_vis = {'min': -20, 'max': -5, 'palette': ['white', 'black']}
        change_vis = {'min': -5, 'max': 5, 'palette': ['red', 'white', 'blue']}
        flood_vis = {'palette': ['0000FF']}  # Blue for flood
        perm_water_vis = {'palette': ['FF0000']}  # Red for permanent water
        
        return {
            "success": True,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km
            },
            "analysis_date": datetime.utcnow().isoformat(),
            "date_range": {
                "pre_flood": f"{pre_flood_start} to {pre_flood_end}",
                "post_flood": f"{post_flood_start} to {post_flood_end}"
            },
            "threshold_used": threshold,
            "flood_statistics": {
                "flood_area_km2": float(flood_area.getInfo()) / 1e6 if flood_area.getInfo() else 0,
                "analysis_radius_km": radius_km
            },
            "satellite_layers": {
                "pre_flood_vh": {
                    "name": "Pre-flood VH (dB)",
                    "tile_url": get_tile_url(pre_flood_vh, pre_vis),
                    "description": "Pre-flood VH polarization backscatter"
                },
                "pre_flood_vv": {
                    "name": "Pre-flood VV (dB)",
                    "tile_url": get_tile_url(pre_flood_vv, pre_vis),
                    "description": "Pre-flood VV polarization backscatter"
                },
                "post_flood_vh": {
                    "name": "Post-flood VH (dB)",
                    "tile_url": get_tile_url(post_flood_vh, pre_vis),
                    "description": "Post-flood VH polarization backscatter"
                },
                "post_flood_vv": {
                    "name": "Post-flood VV (dB)",
                    "tile_url": get_tile_url(post_flood_vv, pre_vis),
                    "description": "Post-flood VV polarization backscatter"
                },
                "vh_change": {
                    "name": "VH Change (dB)",
                    "tile_url": get_tile_url(vh_change, change_vis),
                    "description": "VH polarization change detection"
                },
                "vv_change": {
                    "name": "VV Change (dB)",
                    "tile_url": get_tile_url(vv_change, change_vis),
                    "description": "VV polarization change detection"
                },
                "permanent_water": {
                    "name": "Permanent Water",
                    "tile_url": get_tile_url(permanent_water, perm_water_vis),
                    "description": "Permanent water bodies from JRC dataset"
                },
                "flooded_areas": {
                    "name": "Flooded Areas",
                    "tile_url": get_tile_url(flooded_areas, flood_vis),
                    "description": "Detected flooded areas (excluding permanent water)"
                }
            },
            "data_source": {
                "satellite": "Sentinel-1 GRD",
                "polarization": "VH and VV",
                "resolution": "10m",
                "water_mask": "JRC Global Surface Water",
                "analysis_method": "Change detection with threshold-based classification"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in flood analysis: {str(e)}")

@router.get("/satellite-status")
async def get_satellite_status():
    """Get current satellite data availability status"""
    try:
        # Simple check if GEE is initialized
        try:
            # Try to access a simple GEE object to test initialization
            test_point = ee.Geometry.Point([0, 0])
            test_collection = ee.ImageCollection('COPERNICUS/S1_GRD').limit(1)
            
            # If we get here, GEE is working
            return {
                "satellite_available": True,
                "status": "operational",
                "last_update": datetime.utcnow().isoformat(),
                "data_source": "Sentinel-1 GRD",
                "coverage": "Global",
                "update_frequency": "6-12 days",
                "message": "Google Earth Engine is operational and satellite data is available"
            }
        except Exception as gee_error:
            # GEE is not properly initialized
            return {
                "satellite_available": False,
                "status": "initialization_error",
                "error": str(gee_error),
                "last_update": datetime.utcnow().isoformat(),
                "message": "Google Earth Engine needs to be properly initialized"
            }
            
    except Exception as e:
        return {
            "satellite_available": False,
            "status": "error",
            "error": str(e),
            "last_update": datetime.utcnow().isoformat(),
            "message": "Unable to check satellite status"
        }

@router.get("/historical")
async def get_historical_data(
    latitude: float = Query(..., description="Latitude"),
    longitude: float = Query(..., description="Longitude"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """Get historical satellite data for a location"""
    try:
        point = ee.Geometry.Point([longitude, latitude])
        
        # Get historical VH data
        historical_vh = (ee.ImageCollection('COPERNICUS/S1_GRD')
                        .filterBounds(point)
                        .filterDate(start_date, end_date)
                        .filter(ee.Filter.eq('instrumentMode', 'IW'))
                        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
                        .select('VH'))
        
        # Get historical VV data
        historical_vv = (ee.ImageCollection('COPERNICUS/S1_GRD')
                        .filterBounds(point)
                        .filterDate(start_date, end_date)
                        .filter(ee.Filter.eq('instrumentMode', 'IW'))
                        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
                        .select('VV'))
        
        vh_count = historical_vh.size().getInfo()
        vv_count = historical_vv.size().getInfo()
        
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "date_range": {"start": start_date, "end": end_date},
            "data_availability": {
                "vh_images": vh_count,
                "vv_images": vv_count,
                "total_images": vh_count + vv_count
            },
            "analysis_ready": vh_count > 0 and vv_count > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting historical data: {str(e)}")
