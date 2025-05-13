from pydantic import BaseModel
from typing import List 

class SessionResponse(BaseModel):
    sessionNumber: int # sessionNumber instead of sessionID
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
    meanNoise: float #mean Noise levels
    sessions: List[SessionResponse]
