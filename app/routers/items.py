from tokenize import String
from fastapi import APIRouter, HTTPException
from app.models import PointResponse
from app.services.db import database as supabase
from app.services.db import is_point_active
from app.services.ai_description import request_session_description
from datetime import datetime
import statistics
from typing import Dict, Any


router = APIRouter()

@router.get("/points/{point_id}", response_model=PointResponse)
async def get_point_with_sessions(point_id: int) -> Dict[str, Any]: 
    try:
        # 1. point data
        point_res = supabase.table("points")\
                         .select("*")\
                         .eq("point_id", point_id)\
                         .execute()
        
        if not point_res.data:
            raise HTTPException(status_code=404, detail="Point not found")
        
        point = point_res.data[0]
        
        # 2. get sessions for that point - pero ngayon selecting session_number
        sessions_res = supabase.table("sessions")\
                            .select("session_id, session_number, start_date, end_date")\
                            .eq("point_id", point_id)\
                            .execute()
        
        sessions = []
        all_noise_levels = []  # To store all noise levels for mean calculation
        
        for session in sessions_res.data:
            # 3. get recordings with analysis_text 
            recordings_res = supabase.table("audio_recordings")\
                                  .select("id, db_level, start_time, analysis_text")\
                                  .eq("session_id", session["session_id"])\
                                  .order("id")\
                                  .execute()
            
            session_noise_levels = []  # For session-specific mean
            
            session_data = {
                "sessionNumber": session["session_number"],
                "session_id": session["session_id"],
                "startDate": datetime.strptime(session["start_date"], "%Y-%m-%d").strftime("%B %d, %Y"),
                "endDate": datetime.strptime(session["end_date"], "%Y-%m-%d").strftime("%B %d, %Y"),
                "meanNoiseSession": 0.0,  # Initialize mean
                "data": [],
                "startTimes": [],
                "descriptions": [],

            }
            
            for rec in recordings_res.data:
                noise_level = round(float(rec.get("db_level", 0)), 2)
                session_data["data"].append(noise_level)
                session_noise_levels.append(noise_level)
                all_noise_levels.append(noise_level)
                session_data["startTimes"].append(rec.get("start_time"))
                session_data["descriptions"].append(
                    rec.get("analysis_text", "Normal.")
                )
            
            # Calculate mean for this session
            if session_noise_levels:
                session_data["meanNoiseSession"] = round(statistics.mean(session_noise_levels), 2)
            
            sessions.append(session_data)
        
        # Calculate mean noise for the point (rounded to 2 decimal places)
        mean_noise = round(statistics.mean(all_noise_levels) if all_noise_levels else 0, 2)
        
        # final json format
        response = {
            "pointId": str(point["point_id"]),
            "lat": point["latitude"],
            "lon": point["longitude"],
            "brgy": point["barangay_name"],
            "city": point["city"],
            "meanNoise": mean_noise,
            "sessions": sessions
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geojson/points")
async def get_points_geojson() -> Dict[str, Any]:
    """
    Returns all points in GeoJSON format with aggregated session and noise data.
    """
    try:
        # 1.get points
        points_res = supabase.table("points").select("*").execute()
        if not points_res.data:
            raise HTTPException(status_code=404, detail="No points found")

        features = []
        
        for point in points_res.data:
            # 2. get sessions for that points
            sessions_res = supabase.table("sessions")\
                                .select("session_id")\
                                .eq("point_id", point["point_id"])\
                                .execute()
            session_count = len(sessions_res.data)

            # 3.get all recordings' db_levels for these sessions
            db_levels = []
            isActive = is_point_active(point["point_id"]) 
            if session_count > 0:
                # get all session IDs for this point
                session_ids = [s["session_id"] for s in sessions_res.data]
                
                # get query recordings for sessions
                recordings_res = supabase.table("audio_recordings")\
                                    .select("db_level")\
                                    .in_("session_id", session_ids)\
                                    .execute()
                # extract non-null db levels
                db_levels = [rec["db_level"] for rec in recordings_res.data 
                             if rec["db_level"] is not None]

            # 4)calculate mean noise level (default to 0 if no data)
            mean_noise = statistics.mean(db_levels) if db_levels else 0.0

            # 5.build geojson feature format
            feature = {
                "type": "Feature",
                "id": point["point_id"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["longitude"], point["latitude"]]
                },
                "properties": {
                    "noOfSessions": session_count,
                    "meanNoiseLevel": round(mean_noise, 1),
                    "brgy": point["barangay_name"],
                    "city": point["city"], 
                    "isActive": isActive,
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session_info/{session_id}")
async def get_session_ai_description(session_id: int) -> Any:
    try:
        session_res = supabase.table("audio_recordings")\
                .select("analysis_text")\
                .eq("session_id", session_id)\
                .order("id")\
                .execute()
         
        analysis_texts = "|".join([item["analysis_text"] for item in session_res.data])
        

        return request_session_description(analysis_texts)

   
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    