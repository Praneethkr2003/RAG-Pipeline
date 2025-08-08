from sqlalchemy import create_engine, Column, Integer, String, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os


# Database URL from environment or default to local PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/json_rag_db"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

class JSONChunk(Base):
    """Model for storing JSON chunks with metadata"""
    __tablename__ = "json_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True)
    parent_id = Column(String, index=True, nullable=True)  # For hierarchical data
    source_file = Column(String, index=True)
    chunk_type = Column(String, index=True)  # e.g., 'day_wise', 'week_wise'
    metadata_ = Column(JSONB)  # Store extracted metadata as JSONB
    content = Column(JSONB)  # The actual JSON chunk data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common query patterns
    __table_args__ = (
        # Regular BTREE index for chunk_type (good for equality and range queries)
        Index('idx_chunk_type', 'chunk_type'),
        # GIN index for JSONB metadata (using jsonb_path_ops for efficient JSON path queries)
        Index('idx_metadata', 'metadata_', postgresql_using='gin', postgresql_ops={'metadata_': 'jsonb_path_ops'}),
    )

class PrecomputedAggregate(Base):
    """Model for storing precomputed aggregates"""
    __tablename__ = "precomputed_aggregates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # e.g., 'weekly_glucose_avg'
    key = Column(String, index=True)   # e.g., '2025-W18'
    value = Column(JSONB)               # The computed aggregate value
    metadata_ = Column(JSONB)           # Additional context
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
