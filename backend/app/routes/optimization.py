from ..database import get_db
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Literal, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..crud import list_trains, list_train_sections, list_sections
import pandas as pd

from algorithms.milp_optimizer import MILPOptimizer
from algorithms.rl_optimizer import run_rl_optimizer
from algorithms.comprehensive_hybrid_optimizer import ComprehensiveHybridOptimizer
from backend.app.routes.schedule_postprocess import convert_train_order_to_schedule

router = APIRouter()
OptimizationResult = Dict[str, Any]

async def milp_optimizer(db: AsyncSession) -> OptimizationResult:
    trains = await list_trains(db)
    sections = await list_sections(db)
    train_sections = await list_train_sections(db)

    trains_df = pd.DataFrame([t.__dict__ for t in trains])
    sections_df = pd.DataFrame([s.__dict__ for s in sections])
    train_sections_df = pd.DataFrame([ts.__dict__ for ts in train_sections])

    try:
        optimizer = MILPOptimizer()
        schedule = optimizer.optimize(trains_df, sections_df, train_sections_df)
        return {
            "method": "MILP",
            "optimized_schedule": schedule if schedule else "No optimal solution found",
            "trains_count": len(trains),
            "sections_count": len(train_sections),
        }
    except Exception as exc:
        # Graceful fallback if solver binary is unavailable in this environment
        return {
            "method": "MILP",
            "optimized_schedule": "Unavailable (solver not installed)",
            "error": str(exc),
            "trains_count": len(trains),
            "sections_count": len(train_sections),
        }


async def rl_optimizer(db: AsyncSession) -> OptimizationResult:
    trains = await list_trains(db)
    sections = await list_sections(db)
    train_sections = await list_train_sections(db)

    trains_df = pd.DataFrame([t.__dict__ for t in trains])
    sections_df = pd.DataFrame([s.__dict__ for s in sections])
    train_sections_df = pd.DataFrame([ts.__dict__ for ts in train_sections])

    train_order, score = run_rl_optimizer(trains_df, sections_df, train_sections_df)

    schedule = convert_train_order_to_schedule(train_order, train_sections_df, sections_df)

    return {
        "method": "Reinforcement Learning",
        "optimized_schedule": schedule,
        "score": score,
        "trains_count": len(trains),
        "sections_count": len(train_sections),
    }

async def comprehensive_hybrid_optimizer(db: AsyncSession) -> OptimizationResult:
    trains = await list_trains(db)
    sections = await list_sections(db)
    train_sections = await list_train_sections(db)

    trains_df = pd.DataFrame([t.__dict__ for t in trains])
    sections_df = pd.DataFrame([s.__dict__ for s in sections])
    train_sections_df = pd.DataFrame([ts.__dict__ for ts in train_sections])

    optimizer = ComprehensiveHybridOptimizer()
    result = optimizer.optimize(trains_df, sections_df, train_sections_df)

    return {
        "method": result.method,
        "optimized_schedule": result.schedule,
        "total_delay": result.total_delay,
        "computation_time": result.computation_time,
        "throughput": result.throughput,
        "conflicts_resolved": result.conflicts_resolved,
        "success": result.success,
        "trains_count": len(trains),
        "sections_count": len(train_sections),
    }

@router.get("/optimize/")
async def optimize_schedule(
    method: Literal["milp", "rl", "comprehensive_hybrid"] = Query(default="milp", description="Optimization method to use"),
    db: AsyncSession = Depends(get_db),
):
    if method == "milp":
        result = await milp_optimizer(db)
    elif method == "rl":
        result = await rl_optimizer(db)
    elif method == "comprehensive_hybrid":
        # Add warning about long processing time
        result = await comprehensive_hybrid_optimizer(db)
    else:
        raise HTTPException(status_code=400, detail="Invalid optimization method")

    return {"status": "success", "data": result}

@router.get("/optimize/quick/")
async def quick_optimize_schedule(
    db: AsyncSession = Depends(get_db),
):
    """Ultra-fast endpoint that always returns a lightweight mock response (no solver)."""
    return {
        "status": "success",
        "data": {
            "method": "Test Mode",
            "optimized_schedule": "Mock schedule for testing",
            "total_delay": 95.0,
            "computation_time": 0.02,
            "throughput": 22,
            "conflicts_resolved": 3,
            "success": True,
        },
        "note": "Quick mock response (no solver)",
    }

@router.get("/optimize/test/")
async def test_optimize_schedule(
    db: AsyncSession = Depends(get_db),
):
    """Ultra-fast testing endpoint - returns mock data"""
    return {
        "status": "success", 
        "data": {
            "method": "Test Mode",
            "optimized_schedule": "Mock schedule for testing",
            "total_delay": 150.5,
            "computation_time": 0.1,
            "throughput": 25,
            "conflicts_resolved": 3,
            "success": True,
            "trains_count": 25,
            "sections_count": 11,
            "note": "This is mock data for fast testing - not real optimization"
        }
    }

@router.get("/optimize/status/")
async def optimization_status():
    """Check optimization status without running it"""
    return {
        "status": "available",
        "methods": {
            "milp": "Fast (0.3 seconds)",
            "rl": "Medium (5-10 seconds)", 
            "comprehensive_hybrid": "Very Slow (10+ minutes) - Not recommended for testing"
        },
        "recommended_for_testing": ["milp", "test"]
    }


@router.post("/optimize/scenario")
async def optimize_scenario(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """
    What-if simulation endpoint. Accepts partial overrides for trains/sections
    (e.g., modified delays, capacity) and runs MILP as a fast proxy.
    The database is not mutated; we copy and patch in-memory dataframes.
    """
    # Load base data
    trains = await list_trains(db)
    sections = await list_sections(db)
    train_sections = await list_train_sections(db)

    trains_df = pd.DataFrame([t.__dict__ for t in trains])
    sections_df = pd.DataFrame([s.__dict__ for s in sections])
    train_sections_df = pd.DataFrame([ts.__dict__ for ts in train_sections])

    # Apply overrides if provided
    overrides = payload or {}
    if "trains" in overrides and isinstance(overrides["trains"], list):
        for ov in overrides["trains"]:
            if not isinstance(ov, dict) or "train_id" not in ov:
                continue
            tid = ov["train_id"]
            for col, val in ov.items():
                if col == "train_id":
                    continue
                if col in trains_df.columns:
                    trains_df.loc[trains_df["train_id"] == tid, col] = val

    if "sections" in overrides and isinstance(overrides["sections"], list):
        for ov in overrides["sections"]:
            if not isinstance(ov, dict) or "section_id" not in ov:
                continue
            sid = ov["section_id"]
            for col, val in ov.items():
                if col == "section_id":
                    continue
                if col in sections_df.columns:
                    sections_df.loc[sections_df["section_id"] == sid, col] = val

    optimizer = MILPOptimizer()
    schedule = optimizer.optimize(trains_df, sections_df, train_sections_df)

    # Simple KPIs for scenario
    avg_delay = float(trains_df["delay_minutes"].mean()) if not trains_df.empty else 0.0
    throughput = len(schedule) if isinstance(schedule, list) else 0

    return {
        "status": "success",
        "data": {
            "method": "MILP-Scenario",
            "optimized_schedule": schedule,
            "average_delay_minutes": avg_delay,
            "throughput": throughput,
        },
    }
