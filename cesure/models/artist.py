from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

class Artist(Base, BaseModel):
    __tablename__ = 'artists'

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bio = Column(Text)
    website = Column(String(255))
    social_media = Column(String(255))
    cv = Column(JSON)  # Store CV as JSON
    profile_image = Column(String(255))
    
    # Relationships
    user = relationship("User", back_populates="artist")
    artworks = relationship("Artwork", back_populates="artist")
    competition_entries = relationship("CompetitionEntry", back_populates="artist")