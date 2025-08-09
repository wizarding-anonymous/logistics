import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

# This service connects to the same central database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password@postgres/marketplace")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

async def get_db():
    """
    Dependency to get an async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session
