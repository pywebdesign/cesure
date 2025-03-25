from sqlalchemy import Column, String, DateTime, Text, Float, JSON
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

class Competition(Base, BaseModel):
    __tablename__ = 'competitions'

    title = Column(String(255), nullable=False)
    description = Column(Text)
    rules = Column(Text)
    entry_fee = Column(Float, default=0.0)
    prize_info = Column(JSON)  # Prize details as JSON
    entry_start_date = Column(DateTime(timezone=True), nullable=False)
    entry_end_date = Column(DateTime(timezone=True), nullable=False)
    judging_start_date = Column(DateTime(timezone=True))
    judging_end_date = Column(DateTime(timezone=True))
    results_date = Column(DateTime(timezone=True))
    status = Column(String(50), default='Upcoming')  # Upcoming, Open, Judging, Closed
    image_url = Column(String(255))
    
    # Relationships
    entries = relationship("CompetitionEntry", back_populates="competition")
    judges = relationship("CompetitionJudge", back_populates="competition")
    results = relationship("CompetitionResult", back_populates="competition")