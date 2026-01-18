#!/usr/bin/env python3
"""View all data sources in the database in a formatted table."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from core.database import async_session_factory
from models.data_source import DataSource


async def view_data_sources() -> None:
    """Display all data sources in a formatted table."""
    async with async_session_factory() as session:
        stmt = select(DataSource).order_by(DataSource.created_at.desc())
        result = await session.execute(stmt)
        data_sources = result.scalars().all()
        
        if not data_sources:
            print("📭 No data sources found in the database.")
            print("\nRun 'python scripts/seed_quick.py' to add sample data.")
            return
        
        print(f"\n📊 Found {len(data_sources)} data source(s):\n")
        print("=" * 100)
        
        for i, ds in enumerate(data_sources, 1):
            status = "✅ Active" if ds.is_active else "⏸️  Inactive"
            
            print(f"\n{i}. {ds.name}")
            print(f"   ID:          {ds.id}")
            print(f"   Type:        {ds.source_type}")
            print(f"   Status:      {status}")
            print(f"   Description: {ds.description or 'N/A'}")
            print(f"   Created:     {ds.created_at}")
            
            # Show connection config (hide passwords)
            config = ds.connection_config.copy()
            if "password" in config:
                config["password"] = "***HIDDEN***"
            
            print(f"   Config:      {config}")
            
            if ds.schema_info:
                print(f"   Schema:      ✓ Cached")
            else:
                print(f"   Schema:      ✗ Not cached")
        
        print("\n" + "=" * 100)
        
        # Summary
        active_count = sum(1 for ds in data_sources if ds.is_active)
        inactive_count = len(data_sources) - active_count
        
        print(f"\nSummary: {active_count} active, {inactive_count} inactive")
        
        # Count by type
        type_counts = {}
        for ds in data_sources:
            type_counts[ds.source_type] = type_counts.get(ds.source_type, 0) + 1
        
        print(f"By type: {', '.join(f'{k}: {v}' for k, v in type_counts.items())}")
        print()


if __name__ == "__main__":
    asyncio.run(view_data_sources())
