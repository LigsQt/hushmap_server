from pydantic import BaseModel
from typing import List 

class SessionResponse(BaseModel):
    sessionId: int
    startDate: str
    endDate:str
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