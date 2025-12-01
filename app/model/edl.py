# app/model/edl.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from core.database import Base

class EDLEntry(Base):
    __tablename__ = "edl"

    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(String, index=True, nullable=False)
    edl_name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    frame_rate = Column(Float, default=29.97)
    drop_frame = Column(Boolean, default=False)
    total_events = Column(Integer, default=0)
    validation_status = Column(String, default="pending")
    validation_errors = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
