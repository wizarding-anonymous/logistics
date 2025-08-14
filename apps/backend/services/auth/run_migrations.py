#!/usr/bin/env python3
"""
Simple migration runner for auth service database schema updates
"""

import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Add the service directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password@localhost:5432/marketplace")

async def run_migration(migration_file: str):
    """Run a single migration file"""
    engine = create_async_engine(DATABASE_URL)
    
    migration_path = Path(__file__).parent / "migrations" / migration_file
    
    if not migration_path.exists():
        print(f"Migration file not found: {migration_path}")
        return False
    
    print(f"Running migration: {migration_file}")
    
    try:
        with open(migration_path, 'r') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        async with engine.begin() as conn:
            for statement in statements:
                if statement and not statement.startswith('--'):
                    print(f"Executing: {statement[:100]}...")
                    try:
                        await conn.execute(text(statement))
                    except Exception as e:
                        print(f"Warning: {e}")
                        continue
        
        print(f"Migration {migration_file} completed successfully")
        return True
        
    except Exception as e:
        print(f"Error running migration {migration_file}: {e}")
        return False
    
    finally:
        await engine.dispose()

async def run_all_migrations():
    """Run all pending migrations"""
    migrations_dir = Path(__file__).parent / "migrations"
    
    if not migrations_dir.exists():
        print("No migrations directory found")
        return
    
    # Get all .sql files and sort them
    migration_files = sorted([f.name for f in migrations_dir.glob("*.sql")])
    
    if not migration_files:
        print("No migration files found")
        return
    
    print(f"Found {len(migration_files)} migration(s)")
    
    success_count = 0
    for migration_file in migration_files:
        if await run_migration(migration_file):
            success_count += 1
        else:
            print(f"Migration failed: {migration_file}")
            break
    
    print(f"Completed {success_count}/{len(migration_files)} migrations")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific migration
        migration_file = sys.argv[1]
        asyncio.run(run_migration(migration_file))
    else:
        # Run all migrations
        asyncio.run(run_all_migrations())