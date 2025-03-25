from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base, BaseModel

class User(Base, BaseModel):
    __tablename__ = 'users'

    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Email verification
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # Relationships
    artist = relationship("Artist", back_populates="user", uselist=False)