#!/usr/bin/env python3
"""
Seed Connection Data Script

This script initializes the "external" data sources that the application connects to.
It performs the following:
1. Connects to the local PostgreSQL instance.
2. Creates necessary databases and users if they don't exist:
   - production_db (user: prod_user)
   - analytics (user: analytics_user)
3. Populates these databases with sample tables and data.

Prerequisites:
- Local PostgreSQL running on port 5432
- User running the script has permission to create databases/users (usually 'postgres')
"""

import asyncio
import os
import random
from datetime import datetime, timedelta

import asyncpg
from structlog import get_logger

log = get_logger()

# Configuration matches api/scripts/seed_quick.py
PROD_DB_CONFIG = {
    "database": "production_db",
    "user": "prod_user",
    "password": "secure_password_123",
}

ANALYTICS_DB_CONFIG = {
    "database": "analytics",
    "user": "analytics_user",
    "password": "analytics_pass",
}

# Administrative connection to create DBs/Users
DB_HOST = os.getenv("DB_HOST", "db")
ADMIN_DB_URL = os.getenv("ADMIN_DB_URL", f"postgresql://postgres:postgres@{DB_HOST}:5432/postgres")


async def create_database_and_user(conn, config):
    """Create database and user if they don't exist."""
    db_name = config["database"]
    user = config["user"]
    password = config["password"]

    # Check if user exists
    user_exists = await conn.fetchval("SELECT 1 FROM pg_roles WHERE rolname = $1", user)
    if not user_exists:
        print(f"Creating user {user}...")
        await conn.execute(f"CREATE USER {user} WITH PASSWORD '{password}' CREATEDB")

    # Check if database exists
    db_exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
    if not db_exists:
        print(f"Creating database {db_name}...")
        await conn.execute(f"CREATE DATABASE {db_name} OWNER {user}")
    else:
        print(f"Database {db_name} already exists.")


async def seed_production_db():
    """Seed the production PostgreSQL database."""
    dsn = f"postgresql://{PROD_DB_CONFIG['user']}:{PROD_DB_CONFIG['password']}@{DB_HOST}:5432/{PROD_DB_CONFIG['database']}"
    print(f"Seeding Production DB ({dsn})...")

    try:
        conn = await asyncpg.connect(dsn)
    except Exception as e:
        print(f"Failed to connect to Production DB: {e}")
        return

    try:
        # Create Tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                price DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                country VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER REFERENCES customers(id),
                total_amount DECIMAL(12, 2),
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id),
                product_id INTEGER REFERENCES products(id),
                quantity INTEGER,
                price_at_time DECIMAL(10, 2)
            );
        """)

        # Check if data exists
        count = await conn.fetchval("SELECT COUNT(*) FROM products")
        if count > 0:
            print("Production DB already has data, skipping insertion.")
        else:
            print("Inserting sample data into Production DB...")
            # Insert Products
            products = [
                ("Laptop Pro", "Electronics", 1299.99),
                ("Smartphone X", "Electronics", 999.99),
                ("Wireless Earbuds", "Audio", 149.99),
                ("Office Chair", "Furniture", 299.99),
                ("Coffee Maker", "Kitchen", 89.99),
            ]
            await conn.executemany(
                "INSERT INTO products (name, category, price) VALUES ($1, $2, $3)",
                products
            )

            # Insert Customers
            customers = [
                ("John Doe", "john@example.com", "USA"),
                ("Jane Smith", "jane@example.com", "Canada"),
                ("Alice Johnson", "alice@example.com", "UK"),
                ("Bob Brown", "bob@example.com", "USA"),
            ]
            await conn.executemany(
                "INSERT INTO customers (name, email, country) VALUES ($1, $2, $3)",
                customers
            )

            # Insert Orders (Randomized)
            # Need IDs first
            p_ids = [r['id'] for r in await conn.fetch("SELECT id, price FROM products")]
            c_ids = [r['id'] for r in await conn.fetch("SELECT id FROM customers")]

            for _ in range(20):
                c_id = random.choice(c_ids)
                total = 0

                # Create Order
                order_id = await conn.fetchval(
                    "INSERT INTO orders (customer_id, status, created_at) VALUES ($1, $2, $3) RETURNING id",
                    c_id, random.choice(['completed', 'pending', 'shipped']),
                    datetime.now() - timedelta(days=random.randint(0, 365))
                )

                # Create Order Items
                num_items = random.randint(1, 4)
                for _ in range(num_items):
                    p_id = random.choice(p_ids)
                    price = await conn.fetchval("SELECT price FROM products WHERE id = $1", p_id)
                    qty = random.randint(1, 3)
                    await conn.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES ($1, $2, $3, $4)",
                        order_id, p_id, qty, price
                    )
                    total += float(price) * qty

                # Update Order Total
                await conn.execute("UPDATE orders SET total_amount = $1 WHERE id = $2", total, order_id)

    finally:
        await conn.close()


async def seed_analytics_db():
    """Seed the analytics PostgreSQL database."""
    dsn = f"postgresql://{ANALYTICS_DB_CONFIG['user']}:{ANALYTICS_DB_CONFIG['password']}@{DB_HOST}:5432/{ANALYTICS_DB_CONFIG['database']}"
    print(f"Seeding Analytics DB ({dsn})...")

    try:
        conn = await asyncpg.connect(dsn)
    except Exception as e:
        print(f"Failed to connect to Analytics DB: {e}")
        return

    try:
        # Create Tables
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS page_views (
                id SERIAL PRIMARY KEY,
                url VARCHAR(2048),
                user_id VARCHAR(100),
                session_id VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100),
                properties JSONB,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        count = await conn.fetchval("SELECT COUNT(*) FROM page_views")
        if count > 0:
            print("Analytics DB already has data, skipping insertion.")
        else:
            print("Inserting sample data into Analytics DB...")
            # Insert Page Views
            views = []
            for _ in range(100):
                views.append((
                    f"/page/{random.randint(1, 10)}",
                    f"user_{random.randint(1, 50)}",
                    f"sess_{random.randint(1000, 9999)}",
                    datetime.now() - timedelta(minutes=random.randint(0, 10000))
                ))

            await conn.executemany(
                "INSERT INTO page_views (url, user_id, session_id, timestamp) VALUES ($1, $2, $3, $4)",
                views
            )

    finally:
        await conn.close()


async def main():
    print("Starting World Builder Seeding...")

    # 1. Setup Postgres structure
    postgres_ready = False
    try:
        conn = await asyncpg.connect(ADMIN_DB_URL)
        await create_database_and_user(conn, PROD_DB_CONFIG)
        await create_database_and_user(conn, ANALYTICS_DB_CONFIG)
        await conn.close()
        postgres_ready = True
    except Exception as e:
        print(f"⚠️ Could not connect to default Postgres to create DBs: {e}")
        print("   If you have a specific admin user/pass, set ADMIN_DB_URL env var.")
        print("   Example: ADMIN_DB_URL=postgresql://postgres:mypass@localhost:5432/postgres")
        print("   Skipping Postgres seeding steps...")

    # 2. Seed Databases (only if structure was checked/created)
    if postgres_ready:
        await seed_production_db()
        await seed_analytics_db()

    print("✅ Seeding Process Finished!")


if __name__ == "__main__":
    asyncio.run(main())
