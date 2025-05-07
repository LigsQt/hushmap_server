from pydantic import BaseModel
from typing import List 

class SessionResponse(BaseModel):
    sessionId: int
    date: str
    data: List[float]  # db_level values
    startTimes: List[str]
    descriptions: List[str]

class PointResponse(BaseModel):
    pointId: str
    lat: float
    lon: float
    brgy: str
    city: str
    sessions: List[SessionResponse]