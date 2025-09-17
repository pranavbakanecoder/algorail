from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from backend.app.ai_decision_engine import Train, SectionConflict, ai_decision
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from .. import crud, schemas

router = APIRouter()

class TrainModel(BaseModel):
    train_id: str
    priority: int
    train_type: str
    length: int
    delay: int
    passenger_load: int
    energy_efficiency: float

class ConflictModel(BaseModel):
    section_id: str
    competing_trains: List[str]
    signal_state: str
    weather_condition: str
    platform_availability: Dict[str, bool]
    track_capacity: int

class AiDecisionRequest(BaseModel):
    trains: List[TrainModel]
    conflicts: List[ConflictModel]

@router.post("/ai_decision/")
async def get_ai_recommendation(request: AiDecisionRequest):
    trains = {
        t.train_id: Train(
            t.train_id,
            t.priority,
            t.train_type,
            t.length,
            t.delay,
            t.passenger_load,
            t.energy_efficiency,
        )
        for t in request.trains
    }
    conflicts = [
        SectionConflict(
            c.section_id,
            c.competing_trains,
            c.signal_state,
            c.weather_condition,
            c.platform_availability,
            c.track_capacity,
        )
        for c in request.conflicts
    ]

    recommendations = ai_decision(trains, conflicts)
    return {"recommendations": recommendations}


@router.post("/audit/decision", response_model=schemas.AuditDecision)
async def record_decision(decision: schemas.AuditDecisionBase, db: AsyncSession = Depends(get_db)):
    created = await crud.create_audit_decision(db, decision)
    return created

@router.get("/audit/decision", response_model=list[schemas.AuditDecision])
async def list_decisions(db: AsyncSession = Depends(get_db)):
    items = await crud.list_audit_decisions(db)
    return items
