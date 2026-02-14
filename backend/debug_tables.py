"""
Debug script to check database tables
"""
from database import engine, Base
from sqlalchemy import inspect

# Import all models to register them with Base
from models import User, Deck, Card, UserCardProgress, Review

print("Checking database connection and tables...\n")

# Get inspector
inspector = inspect(engine)

# Check existing tables
existing_tables = inspector.get_table_names()
print(f"Existing tables in database: {existing_tables}\n")

# Check what tables SQLAlchemy thinks should exist
print("Tables defined in SQLAlchemy metadata:")
for table_name in Base.metadata.tables.keys():
    print(f"  - {table_name}")

print("\nCreating all tables...")
Base.metadata.create_all(bind=engine)
print("Create all completed!")

# Check again
existing_tables_after = inspector.get_table_names()
print(f"\nTables after create_all: {existing_tables_after}")
