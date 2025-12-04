# app/model/time_range.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class TimeRange(Base):
    __tablename__ = "time_range"

    id = Column(Integer, primary_key=True, index=True)
    audio_track_id = Column(Integer, ForeignKey("audio_track.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)

    audio_track = relationship("AudioTrack", back_populates="occurrences")
