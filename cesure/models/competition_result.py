from sqlalchemy import Column, Integer, ForeignKey, String, Float, JSON, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

class CompetitionResult(Base, BaseModel):
    __tablename__ = 'competition_results'

    competition_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    entry_id = Column(Integer, ForeignKey('competition_entries.id'), nullable=False)
    placement = Column(Integer)  # 1 for 1st place, 2 for 2nd place, etc.
    award_category = Column(String(100))  # Best in Show, Best Technique, etc.
    score = Column(Float)
    judge_comments = Column(Text)
    prize_details = Column(JSON)  # Prize details as JSON
    
    # Relationships
    competition = relationship("Competition", back_populates="results")
    entry = relationship("CompetitionEntry", back_populates="result")