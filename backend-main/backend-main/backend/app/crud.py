from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import models, schemas
from typing import List, Optional

# Station CRUD (example)
async def get_station(db: AsyncSession, station_id: str):
    result = await db.execute(select(models.Station).where(models.Station.station_id == station_id))
    return result.scalars().first()

async def list_stations(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.Station]:
    result = await db.execute(select(models.Station).offset(skip).limit(limit))
    return result.scalars().all()

async def create_station(db: AsyncSession, station: schemas.StationBase):
    db_station = models.Station(**station.dict())
    db.add(db_station)
    await db.commit()
    await db.refresh(db_station)
    return db_station

# Train CRUD
async def get_train(db: AsyncSession, train_id: str):
    result = await db.execute(select(models.Train).where(models.Train.train_id == train_id))
    return result.scalars().first()

async def list_trains(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.Train]:
    result = await db.execute(select(models.Train).offset(skip).limit(limit))
    return result.scalars().all()

async def create_train(db: AsyncSession, train: schemas.TrainBase):
    db_train = models.Train(**train.dict())
    db.add(db_train)
    await db.commit()
    await db.refresh(db_train)
    return db_train

# Section CRUD (added)
async def list_sections(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.Section]:
    result = await db.execute(select(models.Section).offset(skip).limit(limit))
    return result.scalars().all()

# TrainSection CRUD
async def get_train_section(db: AsyncSession, section_id: int):
    result = await db.execute(select(models.TrainSection).where(models.TrainSection.id == section_id))
    return result.scalars().first()

async def list_train_sections(db: AsyncSession, train_id: Optional[str] = None):
    query = select(models.TrainSection)
    if train_id:
        query = query.where(models.TrainSection.train_id == train_id)
    result = await db.execute(query)
    return result.scalars().all()

async def create_train_section(db: AsyncSession, train_section: schemas.TrainSectionCreate):
    db_ts = models.TrainSection(**train_section.dict())
    db.add(db_ts)
    await db.commit()
    await db.refresh(db_ts)
    return db_ts

# Disruptions CRUD (to support /disruptions/ endpoint)
async def list_disruptions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[schemas.Disruption]:
    result = await db.execute(select(models.Disruption).offset(skip).limit(limit))
    return result.scalars().all()

async def create_disruption(db: AsyncSession, disruption: schemas.DisruptionBase):
    db_obj = models.Disruption(**disruption.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# Audit CRUD
async def create_audit_decision(db: AsyncSession, decision: schemas.AuditDecisionBase) -> models.AuditDecision:
    db_obj = models.AuditDecision(**decision.dict())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def list_audit_decisions(db: AsyncSession, since: Optional[str] = None) -> List[models.AuditDecision]:
    # For simplicity, not filtering by since here (no datetime type). Could be added later.
    result = await db.execute(select(models.AuditDecision))
    return result.scalars().all()
