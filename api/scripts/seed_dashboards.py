#!/usr/bin/env python3
"""Seed script for populating the database with sample dashboards."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import async_session_factory
from models.dashboard import Dashboard
from models.data_source import DataSource


async def clear_existing_dashboards() -> None:
    """Clear all existing dashboards from the database."""
    async with async_session_factory() as session:
        stmt = select(Dashboard)
        result = await session.execute(stmt)
        dashboards = result.scalars().all()
        
        for d in dashboards:
            await session.delete(d)
        
        await session.commit()
        print(f"🗑️  Cleared {len(dashboards)} existing dashboards")


async def seed_dashboards() -> None:
    """Seed the database with sample dashboards."""
    
    async with async_session_factory() as session:
        # Fetch existing data sources to associate
        stmt = select(DataSource).where(DataSource.is_active == True)
        result = await session.execute(stmt)
        data_sources = result.scalars().all()
        
        if not data_sources:
            print("⚠️  No active data sources found. Please seed data sources first.")
            return

        sample_dashboards = [
            {
                "title": "Inventory & Operations",
                "description": "Real-time look at product inventory and archive data. This dashboard should provide high level metrics at the top, and graphs below. It should include a bar chart of inventory levels, a line chart of sales over time, and a table of recent orders.",
                "data_sources": [ds for ds in data_sources if "Inventory" in ds.name or "Database" in ds.name],
            },
            {
                "title": "Executive Overview",
                "data_sources": [data_sources[0]],
            },
            {
                "title": "Sales Performance",
                "description": "Overview of sales metrics and customer demographics. This dashboard should provide high level metrics at the top, and graphs below. It should include a bar chart of inventory levels, a line chart of sales over time, and a table of recent orders.",
                "data_sources": [ds for ds in data_sources if "Sales" in ds.name or "Demographics" in ds.name],
            },
        ]
        
        created_count = 0
        for d_data in sample_dashboards:
            dashboard = Dashboard(**d_data)
            session.add(dashboard)
            created_count += 1
            print(f"✅ Creating Dashboard: {d_data['title']} (with {len(d_data['data_sources'])} sources)")
        
        await session.commit()
        print(f"\n🎉 Successfully seeded {created_count} dashboards!")


async def main() -> None:
    """Main function to run the seeding process."""
    print("=" * 60)
    print("🌱 Dashboard Seeding Script")
    print("=" * 60)
    print()
    
    # In a real scenario we might want confirmation, but for this task we just run it.
    await clear_existing_dashboards()
    print()
    await seed_dashboards()
    print()
    print("=" * 60)
    print("✨ Seeding complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
