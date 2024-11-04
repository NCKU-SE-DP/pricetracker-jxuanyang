from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for models
Base = declarative_base()

# Database engine and session
engine = create_engine("sqlite:///news_database.db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def session_opener():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
