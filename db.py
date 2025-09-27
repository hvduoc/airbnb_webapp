import os
from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
else:
    engine = create_engine("sqlite:///app.db", connect_args={"check_same_thread": False})

def init_db():
    from models import Building, Property, Channel, Booking, ImportLog
    SQLModel.metadata.create_all(engine)

def get_session():
    """FastAPI dependency to get database session"""
    with Session(engine) as session:
        yield session

@contextmanager  
def get_session_context():
    """Context manager for manual session handling"""
    with Session(engine) as session:
        yield session
