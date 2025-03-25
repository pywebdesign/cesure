from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, JSON, String
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

class CompetitionEntry(Base, BaseModel):
    __tablename__ = 'competition_entries'

    competition_id = Column(Integer, ForeignKey('competitions.id'), nullable=False)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    artwork_id = Column(Integer, ForeignKey('artworks.id'), nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False)
    artist_statement = Column(Text)
    status = Column(String(50), default='Submitted')  # Submitted, Approved, Rejected
    additional_info = Column(JSON)  # Additional info as JSON
    
    # Relationships
    competition = relationship("Competition", back_populates="entries")
    artist = relationship("Artist", back_populates="competition_entries")
    artwork = relationship("Artwork", back_populates="competition_entries")
    result = relationship("CompetitionResult", back_populates="entry", uselist=False)