from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from . import models, schemas, crud, database, import_data
from .routes import optimization
from .routes import live_data_routes

from .routes import ai_routes
from .routes import conflict_alerts_routes


app = FastAPI(title="AlgoRail Backend API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8080",  # Alternative frontend port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Include existing routers inside a function to avoid circular imports
def include_routes():
    from .routes import optimization
    app.include_router(optimization.router)
    # Include AI decision router with prefix /api (or without prefix if preferred)
    app.include_router(ai_routes.router, prefix="/api")


include_routes()
app.include_router(live_data_routes.router)
app.include_router(conflict_alerts_routes.router)

async def get_db():
    async with database.SessionLocal() as session:
        yield session


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "AlgoRail Backend API is running"}


@app.get("/api/status", tags=["Status"])
async def get_status():
    return {"message": "Backend is running", "status": "healthy"}


@app.get("/stations/", response_model=List[schemas.Station])
async def read_stations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.list_stations(db)


@app.post("/stations/", response_model=schemas.Station)
async def create_station(station: schemas.StationBase, db: AsyncSession = Depends(get_db)):
    return await crud.create_station(db, station)


@app.get("/sections/", response_model=List[schemas.Section])
async def read_sections(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.list_sections(db)


@app.post("/sections/", response_model=schemas.Section)
async def create_section(section: schemas.SectionBase, db: AsyncSession = Depends(get_db)):
    return await crud.create_section(db, section)


@app.get("/disruptions/", response_model=List[schemas.Disruption])
async def read_disruptions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.list_disruptions(db)


@app.post("/disruptions/", response_model=schemas.Disruption)
async def create_disruption(disruption: schemas.DisruptionBase, db: AsyncSession = Depends(get_db)):
    return await crud.create_disruption(db, disruption)


@app.get("/trains/", response_model=List[schemas.Train])
async def read_trains(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.list_trains(db)


@app.post("/trains/", response_model=schemas.Train)
async def create_train(train: schemas.TrainBase, db: AsyncSession = Depends(get_db)):
    db_train = await crud.get_train(db, train.train_id)
    if db_train:
        raise HTTPException(status_code=400, detail="Train already exists")
    return await crud.create_train(db, train)


@app.post("/train_sections/", response_model=schemas.TrainSection)
async def create_train_section(train_section: schemas.TrainSectionCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_train_section(db, train_section)


@app.get("/train_sections/", response_model=List[schemas.TrainSection])
async def read_train_sections(train_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    return await crud.list_train_sections(db, train_id)


@app.post("/import-data/")
async def trigger_import():
    await import_data.main()
    return {"message": "Data import complete."}


@app.get("/kpis/current", response_model=schemas.KPIResponse)
async def get_current_kpis(db: AsyncSession = Depends(get_db)):
    trains = await crud.list_trains(db)
    total = len(trains)
    delayed = sum(1 for t in trains if (t.delay_minutes or 0) > 0)
    avg_delay = (sum((t.delay_minutes or 0) for t in trains) / total) if total else 0.0
    # Simple placeholders; can refine using schedule + sections
    throughput = float(total) / 2.0 if total else 0.0
    utilization = 65.0 if total else 0.0
    return schemas.KPIResponse(
        total_trains=total,
        delayed_trains=delayed,
        average_delay_minutes=round(avg_delay, 2),
        throughput_trains_per_hour=round(throughput, 2),
        section_utilization_pct=utilization,
    )
