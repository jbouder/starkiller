#!/usr/bin/env python3
"""Seed script for populating the database with sample data sources."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from core.database import async_session_factory
from models.data_source import DataSource


async def clear_existing_data_sources() -> None:
    """Clear all existing data sources from the database."""
    async with async_session_factory() as session:
        stmt = select(DataSource)
        result = await session.execute(stmt)
        data_sources = result.scalars().all()
        
        for ds in data_sources:
            await session.delete(ds)
        
        await session.commit()
        print(f"🗑️  Cleared {len(data_sources)} existing data sources")


async def seed_data_sources() -> None:
    """Seed the database with sample data sources."""
    
    sample_data_sources = [
        # PostgreSQL data sources
        {
            "name": "Production PostgreSQL",
            "description": "Main production database for customer data",
            "source_type": "postgresql",
            "connection_config": {
                "host": "host.docker.internal",
                "port": 5432,
                "database": "production_db",
                "username": "postgres",
                "password": "postgres",
                "ssl_mode": "require",
            },
            "is_active": True,
        },
        {
            "name": "Analytics Database",
            "description": "PostgreSQL database for analytics and reporting",
            "source_type": "postgresql",
            "connection_config": {
                "host": "host.docker.internal",
                "port": 5432,
                "database": "analytics",
                "username": "postgres",
                "password": "postgres",
                "ssl_mode": "prefer",
            },
            "is_active": True,
        },
        {
            "name": "Development PostgreSQL",
            "description": "Development database for testing queries",
            "source_type": "postgresql",
            "connection_config": {
                "host": "host.docker.internal",
                "port": 5432,
                "database": "dev_db",
                "username": "postgres",
                "password": "postgres",
            },
            "is_active": True,
        },
        {
            "name": "Legacy Database",
            "description": "Old PostgreSQL database - deprecated",
            "source_type": "postgresql",
            "connection_config": {
                "host": "host.docker.internal",
                "port": 5432,
                "database": "legacy_db",
                "username": "postgres",
                "password": "postgres",
            },
            "is_active": False,
        },
        # CSV data sources
        {
            "name": "Sales Data CSV",
            "description": "Monthly sales data export",
            "source_type": "csv",
            "connection_config": {
                "file_path": "/app/mock_data/sales/monthly_sales_2024.csv",
            },
            "is_active": True,
        },
        {
            "name": "Customer Demographics",
            "description": "Customer demographic information from marketing",
            "source_type": "csv",
            "connection_config": {
                "file_path": "/app/mock_data/customers/demographics.csv",
            },
            "is_active": True,
        },
        {
            "name": "Product Inventory",
            "description": "Current product inventory snapshot",
            "source_type": "csv",
            "connection_config": {
                "file_path": "/app/mock_data/inventory/products_inventory.csv",
            },
            "is_active": True,
        },
        {
            "name": "Historical Orders",
            "description": "Archive of historical order data",
            "source_type": "csv",
            "connection_config": {
                "file_path": "/app/mock_data/archive/orders_2023.csv",
            },
            "is_active": False,
        },
    ]
    
    async with async_session_factory() as session:
        created_count = 0
        
        for ds_data in sample_data_sources:
            data_source = DataSource(**ds_data)
            session.add(data_source)
            created_count += 1
            
            status = "✅" if ds_data["is_active"] else "⏸️ "
            print(f"{status} Creating: {ds_data['name']} ({ds_data['source_type']})")
        
        await session.commit()
        print(f"\n🎉 Successfully seeded {created_count} data sources!")


async def main() -> None:
    """Main function to run the seeding process."""
    print("=" * 60)
    print("🌱 Data Source Seeding Script")
    print("=" * 60)
    print()
    
    # Ask for confirmation before clearing
    response = input("⚠️  This will clear existing data sources. Continue? (y/N): ")
    if response.lower() != "y":
        print("❌ Seeding cancelled.")
        return
    
    print()
    await clear_existing_data_sources()
    print()
    await seed_data_sources()
    print()
    print("=" * 60)
    print("✨ Seeding complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
