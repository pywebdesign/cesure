from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os

# Database connection
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:psql@postgres:5432/postgres")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BaseModel(object):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())