import pandas as pd
import asyncio
from .database import engine, SessionLocal
from . import models
from sqlalchemy.ext.asyncio import AsyncSession


async def import_stations():
    df = pd.read_csv("data/stations.csv")  # Change path as needed
    async with SessionLocal() as session:
        for _, row in df.iterrows():
            station = models.Station(
                station_id=row.station_id,
                display_name=row.display_name,
                lat=row.lat,
                lon=row.lon,
                platforms=int(row.platforms),
            )
            session.add(station)
        await session.commit()


async def import_sections():
    df = pd.read_csv("data/sections.csv")  # Change path as needed
    async with SessionLocal() as session:
        for _, row in df.iterrows():
            section = models.Section(
                section_id=row.section_id,
                from_station=row.from_station,
                to_station=row.to_station,
                length_km=row.length_km,
                track_type=row.track_type,
                max_trains_allowed=row.max_trains_allowed,
                block_length_km=row.block_length_km,
                num_blocks=row.num_blocks,
                junction_flag=row.junction_flag.lower() == "yes",
            )
            session.add(section)
        await session.commit()


async def import_disruptions():
    df = pd.read_csv("data/disruptions.csv")  # Change path as needed
    async with SessionLocal() as session:
        for _, row in df.iterrows():
            disruption = models.Disruption(
                disruption_id=row.disruption_id,
                type=row.type,
                location_section=row.location_section,
                start_time=row.start_time,
                duration_minutes=row.duration_minutes,
                severity=row.severity,
            )
            session.add(disruption)
        await session.commit()


async def import_trains():
    df = pd.read_csv("data/trains.csv")  # Change path as needed
    async with SessionLocal() as session:
        for _, row in df.iterrows():
            train = models.Train(
                train_id=row.train_id,
                train_name=row.train_name,
                train_type=row.train_type,
                priority=row.priority,
                max_speed_kmph=row.max_speed_kmph,
                platform_requirement=row.platform_requirement == "Yes",
                scheduled_start_time=row.scheduled_start_time,
                origin_station=row.origin_station,
                destination_station=row.destination_station,
                route_nodes=eval(row.route_nodes),  # Assumes JSON-like strings
                route_sections=eval(row.route_sections),
                delay_minutes=row.delay_minutes,
            )
            session.add(train)
        await session.commit()


async def import_train_sections():
    df = pd.read_csv("data/train_sections.csv")  # Change path as needed
    async with SessionLocal() as session:
        for _, row in df.iterrows():
            ts = models.TrainSection(
                train_id=row.train_id,
                section_id=row.section_id,
                scheduled_entry_time=row.scheduled_entry_time,
                scheduled_exit_time=row.scheduled_exit_time,
                planned_stop_next_station=int(row.planned_stop_next_station),
                dwell_minutes_next_station=int(row.dwell_minutes_next_station),
            )
            session.add(ts)
        await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    await import_stations()
    await import_sections()
    await import_disruptions()
    await import_trains()
    await import_train_sections()


if __name__ == "__main__":
    asyncio.run(main())
