"""
Database initialization utilities
Functions to create/drop tables and seed initial data
"""
from app.db.session import engine, Base
from app.models import user, menu, fuzzy, rating, research
from app.core.config import settings


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_all_tables():
    """
    Drop all database tables
    WARNING: This will delete all data!
    """
    print("WARNING: Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped.")


def reset_db():
    """
    Reset database: drop all tables and recreate them
    WARNING: This will delete all data!
    """
    print("Resetting database...")
    drop_all_tables()
    init_db()
    print("Database reset complete!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            init_db()
        elif command == "drop":
            drop_all_tables()
        elif command == "reset":
            reset_db()
        else:
            print("Usage: python init_db.py [create|drop|reset]")
    else:
        print("Creating tables...")
        init_db()
