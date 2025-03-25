from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship

from .base import Base, BaseModel

class Event(Base, BaseModel):
    __tablename__ = 'events'

    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    location = Column(String(255))
    image_url = Column(String(255))
    event_type = Column(String(50))  # Exhibition, Workshop, etc.
    is_public = Column(String(1), default='Y')  # Y/N