from sqlalchemy import Column, String, Integer, Float, Enum, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import enum

class TrainStatusEnum(enum.Enum):
    on_time = "on-time"
    delayed = "delayed"
    early = "early"

class Station(Base):
    __tablename__ = "stations"

    station_id = Column(String, primary_key=True)
    display_name = Column(String, nullable=False)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    platforms = Column(Integer, default=1)

class Section(Base):
    __tablename__ = "sections"

    section_id = Column(String, primary_key=True)
    from_station = Column(String, nullable=False)
    to_station = Column(String, nullable=False)
    length_km = Column(Float)
    track_type = Column(String)
    max_trains_allowed = Column(Integer)
    block_length_km = Column(Float)
    num_blocks = Column(Integer)
    junction_flag = Column(Boolean)

class Disruption(Base):
    __tablename__ = "disruptions"

    disruption_id = Column(String, primary_key=True)
    type = Column(String)
    location_section = Column(String)
    start_time = Column(String)  # for simplicity store time as string, can be datetime
    duration_minutes = Column(Integer)
    severity = Column(String)

class Train(Base):
    __tablename__ = "trains"

    train_id = Column(String, primary_key=True)
    train_name = Column(String)
    train_type = Column(String)
    priority = Column(Integer)
    max_speed_kmph = Column(Integer)
    platform_requirement = Column(Boolean)
    scheduled_start_time = Column(String)
    origin_station = Column(String)
    destination_station = Column(String)
    route_nodes = Column(JSON)
    route_sections = Column(JSON)
    delay_minutes = Column(Integer)

    # Added relationship to TrainSection model
    train_sections = relationship("TrainSection", back_populates="train")

class TrainSection(Base):
    __tablename__ = "train_sections"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    train_id = Column(String, ForeignKey("trains.train_id"), nullable=False)
    section_id = Column(String, ForeignKey("sections.section_id"), nullable=False)
    scheduled_entry_time = Column(String)
    scheduled_exit_time = Column(String)
    planned_stop_next_station = Column(Integer)
    dwell_minutes_next_station = Column(Integer)

    train = relationship("Train", back_populates="train_sections")
    section = relationship("Section")

class AuditDecision(Base):
    __tablename__ = "audit_decisions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    alert_id = Column(String)
    section_id = Column(String)
    competing_trains = Column(JSON)  # list[str]
    chosen_train_id = Column(String)
    reason = Column(String)
    created_at = Column(String)  # ISO timestamp string for simplicity

