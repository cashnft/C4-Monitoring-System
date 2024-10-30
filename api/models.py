import asyncio
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create base class for declarative models
Base = declarative_base()

#Metric model
class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String, nullable=False)
    metric_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

#log model
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String, nullable=False)
    level = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

#trace model
class Trace(Base):
    __tablename__ = "traces"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String, nullable=False)
    service = Column(String, nullable=False)
    operation = Column(String, nullable=False)
    duration = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)

# Database configuration
DATABASE_URL = "postgresql+asyncpg://user:password@db:5432/monitoring_db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# database initialization function
async def init_db(retries=5, delay=5):
    for attempt in range(retries):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as e:
            if attempt == retries - 1:
                raise e
            print(f"Database connection attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            await asyncio.sleep(delay)

# Helper function to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()