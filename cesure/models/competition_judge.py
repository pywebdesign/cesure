from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

class CompetitionJudge(Base, BaseModel):
    __tablename__ = 'competition_judges'

    competition_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    bio = Column(Text)
    website = Column(String(255))
    role = Column(String(100))  # Head Judge, Guest Judge, etc.
    
    # Relationships
    competition = relationship("Competition", back_populates="judges")