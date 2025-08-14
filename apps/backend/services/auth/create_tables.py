#!/usr/bin/env python3
"""
Create database tables using SQLAlchemy models
"""

import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Add the service directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password@localhost:5432/marketplace")

async def create_tables():
    """Create all tables using SQLAlchemy models"""
    try:
        from models import Base
        
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        print("Creating database tables...")
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        print("✓ All tables created successfully!")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    sys.exit(0 if success else 1)