from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from backend.app import crud, schemas, models
from backend.app.database import get_db

router = APIRouter(prefix="/trains", tags=["trains"])

# Get all trains
@router.get("/", response_model=List[schemas.Train])
async def read_trains(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    trains = await crud.list_trains(db, skip=skip, limit=limit)
    return trains

# Get a single train by ID
@router.get("/{train_id}", response_model=schemas.Train)
async def read_train(train_id: str, db: AsyncSession = Depends(get_db)):
    train = await crud.get_train(db, train_id)
    if train is None:
        raise HTTPException(status_code=404, detail="Train not found")
    return train

# Create a new train
@router.post("/", response_model=schemas.Train)
async def create_train(train: schemas.TrainBase, db: AsyncSession = Depends(get_db)):
    db_train = await crud.create_train(db, train)
    return db_train

# Get train sections optionally by train_id
@router.get("/sections/", response_model=List[schemas.TrainSection])
async def read_train_sections(train_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    sections = await crud.list_train_sections(db, train_id)
    return sections

# Create a new train section
@router.post("/sections/", response_model=schemas.TrainSection)
async def create_train_section(train_section: schemas.TrainSectionCreate, db: AsyncSession = Depends(get_db)):
    db_section = await crud.create_train_section(db, train_section)
    return db_section
