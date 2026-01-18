# Database Seeding Scripts

This directory contains scripts for seeding the database with sample data.

## Available Scripts

### 1. `seed_data_sources.py` - Full Seeding Script

Seeds the database with 8 comprehensive sample data sources (4 PostgreSQL + 4 CSV).

**Features:**

- Interactive confirmation prompt before clearing data
- Detailed progress output with emojis
- Includes both active and inactive data sources
- More realistic variety of data sources

**Usage:**

```bash
python scripts/seed_data_sources.py
```

**Sample Data Sources:**

- Production PostgreSQL
- Analytics Database
- Development PostgreSQL
- Legacy Database (inactive)
- Sales Data CSV
- Customer Demographics CSV
- Product Inventory CSV
- Historical Orders CSV (inactive)

---

### 2. `seed_quick.py` - Quick Seeding Script

Seeds the database with 3 essential data sources for quick testing.

**Features:**

- No confirmation required (auto-clears and seeds)
- Minimal output
- Perfect for automated testing and CI/CD
- Fast execution

**Usage:**

```bash
python scripts/seed_quick.py
```

**Sample Data Sources:**

- Production PostgreSQL
- Analytics Database
- Sales Data CSV

---

## Verification

After running either script, verify the data was seeded correctly:

```bash
# List all data sources
curl http://localhost:8000/api/v1/data-sources | python -m json.tool

# Get a specific data source (replace {id} with actual ID)
curl http://localhost:8000/api/v1/data-sources/{id} | python -m json.tool
```

## Notes

- Both scripts will **clear all existing data sources** before seeding
- Connection credentials in the seed data are examples only
- CSV file paths are placeholder paths
- The scripts use async SQLAlchemy sessions directly (not the API)
- Make sure your database is initialized before running these scripts

## Integration with Tests

You can import and use these scripts in your test setup:

```python
from scripts.seed_quick import seed_quick

async def test_setup():
    await seed_quick()
    # Your tests here...
```
