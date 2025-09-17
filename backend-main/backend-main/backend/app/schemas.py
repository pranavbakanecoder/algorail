from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class TrainStatusEnum(str, Enum):
    on_time = "on-time"
    delayed = "delayed"
    early = "early"

class StationBase(BaseModel):
    station_id: str
    display_name: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    platforms: Optional[int] = 1

class Station(StationBase):
    class Config:
        orm_mode = True

class SectionBase(BaseModel):
    section_id: str
    from_station: str
    to_station: str
    length_km: float
    track_type: str
    max_trains_allowed: int
    block_length_km: float
    num_blocks: int
    junction_flag: Optional[bool]

class Section(SectionBase):
    class Config:
        orm_mode = True

class DisruptionBase(BaseModel):
    disruption_id: str
    type: str
    location_section: str
    start_time: str
    duration_minutes: int
    severity: str

class Disruption(DisruptionBase):
    class Config:
        orm_mode = True

class TrainBase(BaseModel):
    train_id: str
    train_name: str
    train_type: str
    priority: int
    max_speed_kmph: int
    platform_requirement: bool
    scheduled_start_time: str
    origin_station: str
    destination_station: str
    route_nodes: List[str]
    route_sections: List[str]
    delay_minutes: int

class Train(TrainBase):
    class Config:
        orm_mode = True


class TrainSectionBase(BaseModel):
    train_id: str
    section_id: str
    scheduled_entry_time: str
    scheduled_exit_time: str
    planned_stop_next_station: int
    dwell_minutes_next_station: int

class TrainSectionCreate(TrainSectionBase):
    pass

class TrainSection(TrainSectionBase):
    id: int

    class Config:
        orm_mode = True


class AuditDecisionBase(BaseModel):
    alert_id: str
    section_id: str
    competing_trains: List[str]
    chosen_train_id: str
    reason: str
    created_at: str

class AuditDecision(AuditDecisionBase):
    id: int

    class Config:
        orm_mode = True


class KPIResponse(BaseModel):
    total_trains: int
    delayed_trains: int
    average_delay_minutes: float
    throughput_trains_per_hour: float
    section_utilization_pct: float
