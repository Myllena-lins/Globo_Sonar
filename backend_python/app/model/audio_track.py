# app/model/audio_track.py
from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from core.database import Base

class AudioTrack(Base):
    __tablename__ = "audio_track"

    id = Column(Integer, primary_key=True, index=True)
    mxf_id = Column(Integer, ForeignKey("mxf.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    album = Column(String)
    year = Column(String)
    authors = Column(ARRAY(String))
    genres = Column(ARRAY(String))
    isrc = Column(String)
    gmusic = Column(String)
    image_url = Column(String)

    occurrences = relationship("TimeRange", back_populates="audio_track", cascade="all, delete-orphan")
    mxf = relationship("MXFFile", back_populates="audio_tracks")
