from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Define Pydantic model for live train data
class LiveTrain(BaseModel):
    train_id: str
    current_section: str
    position_km: float
    speed_kmph: float
    delay_minutes: int

# API endpoint returning static dummy live train positions
@router.get("/live-trains/", response_model=List[LiveTrain])
async def get_live_trains():
    # Static dummy data simulating live train positions
    trains = [
        {
            "train_id": "T001",
            "current_section": "S03",
            "position_km": 12.5,
            "speed_kmph": 75.0,
            "delay_minutes": 0
        },
        {
            "train_id": "T002",
            "current_section": "S05",
            "position_km": 30.1,
            "speed_kmph": 60.0,
            "delay_minutes": 5
        },
        {
            "train_id": "T003",
            "current_section": "S01",
            "position_km": 0.0,
            "speed_kmph": 0.0,
            "delay_minutes": 15
        }
    ]
    return trains

