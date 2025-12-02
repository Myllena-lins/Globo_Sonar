# app/model/mxf_file.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class MXFFile(Base):
    __tablename__ = "mxf"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    path = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, server_default=func.now())

    audio_tracks = relationship("AudioTrack", back_populates="mxf", cascade="all, delete-orphan")
