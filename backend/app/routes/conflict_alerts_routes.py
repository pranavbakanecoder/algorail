from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

# Define model for conflict alert
class ConflictAlert(BaseModel):
    alert_id: str
    section_id: str
    conflicting_trains: List[str]
    alert_type: str  # e.g., "Track Block", "Delay", "Signal Failure"
    severity_level: int  # 1=Low, 5=High
    timestamp: str  # ISO format datetime string

# Static dummy conflict alerts
@router.get("/conflict-alerts/", response_model=List[ConflictAlert])
async def get_conflict_alerts():
    alerts = [
        {
            "alert_id": "A001",
            "section_id": "S03",
            "conflicting_trains": ["T001", "T005"],
            "alert_type": "Track Block",
            "severity_level": 4,
            "timestamp": "2025-09-12T12:30:00Z"
        },
        {
            "alert_id": "A002",
            "section_id": "S07",
            "conflicting_trains": ["T002", "T008"],
            "alert_type": "Signal Failure",
            "severity_level": 5,
            "timestamp": "2025-09-12T12:32:00Z"
        }
    ]
    return alerts
