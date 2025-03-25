from sqlalchemy import Column, String, Integer, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

class Artwork(Base, BaseModel):
    __tablename__ = 'artworks'

    title = Column(String(255), nullable=False)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)
    medium = Column(String(255))
    dimensions = Column(String(255))
    year_created = Column(Integer)
    description = Column(Text)
    image_url = Column(String(255))
    price = Column(Float)
    is_for_sale = Column(Integer, default=0)  # 0: Not for sale, 1: For sale, 2: Sold
    additional_info = Column(JSON)  # Additional info as JSON
    
    # Relationships
    artist = relationship("Artist", back_populates="artworks")
    competition_entries = relationship("CompetitionEntry", back_populates="artwork")