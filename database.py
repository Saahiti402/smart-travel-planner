from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL=postgresql://USERNAME:team123@172.25.84.112:5432/smart_travel_planner
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# create tables
from models import *

Base.metadata.create_all(bind=engine)

print("Tables created successfully")
