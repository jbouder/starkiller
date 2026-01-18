#!/usr/bin/env python3
"""Quick seed script - no confirmation required (useful for testing)."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from core.database import async_session_factory
from models.data_source import DataSource


async def seed_quick() -> None:
    """Quickly seed the database with sample data sources."""
    
    sample_data_sources = [
        {
            "name": "Production PostgreSQL",
            "description": "Main production database for customer data",
            "source_type": "postgresql",
            "connection_config": {
                "host": "localhost",
                "port": 5432,
                "database": "production_db",
                "username": "prod_user",
                "password": "secure_password_123",
                "ssl_mode": "require",
            },
            "is_active": True,
        },
        {
            "name": "Analytics Database",
            "description": "PostgreSQL database for analytics and reporting",
            "source_type": "postgresql",
            "connection_config": {
                "host": "analytics.example.com",
                "port": 5432,
                "database": "analytics",
                "username": "analytics_user",
                "password": "analytics_pass",
            },
            "is_active": True,
        },
        {
            "name": "Sales Data CSV",
            "description": "Monthly sales data export",
            "source_type": "csv",
            "connection_config": {
                "file_path": "/data/sales/monthly_sales_2024.csv",
            },
            "is_active": True,
        },
    ]
    
    async with async_session_factory() as session:
        # Clear existing
        stmt = select(DataSource)
        result = await session.execute(stmt)
        existing = result.scalars().all()
        for ds in existing:
            await session.delete(ds)
        
        # Add new
        for ds_data in sample_data_sources:
            data_source = DataSource(**ds_data)
            session.add(data_source)
        
        await session.commit()
        print(f"✅ Seeded {len(sample_data_sources)} data sources")


if __name__ == "__main__":
    asyncio.run(seed_quick())
