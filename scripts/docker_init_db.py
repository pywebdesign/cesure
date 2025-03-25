#!/usr/bin/env python3
"""
Docker-compatible database initialization script that runs Alembic migrations
"""

import os
import subprocess
import sys
import time
from sqlalchemy import create_engine, exc, text

def run_command(command, check=True):
    """Run a shell command and return its output."""
    print(command)
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def check_postgres_connection(connection_string):
    """Check if we can connect to PostgreSQL using SQLAlchemy."""
    admin_engine = create_engine(connection_string)
    
    for attempt in range(10):
        try:
            with admin_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception as e:
            print(f"Waiting for PostgreSQL to be ready (attempt {attempt+1}/10)...")
            print(f"Connection error: {e}")
            time.sleep(3)
    
    return False

def create_database_if_not_exists(connection_string, db_name):
    """Create the database if it doesn't exist using SQLAlchemy."""
    # Connection string for postgres default database
    admin_engine = create_engine(connection_string)
    
    try:
        # Check if database exists
        with admin_engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if result.rowcount == 0:
                print(f"Database {db_name} doesn't exist. Creating it...")
                # Commit the transaction before executing CREATE DATABASE
                conn.execute(text("COMMIT"))
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"Database {db_name} created successfully.")
            else:
                print(f"Database {db_name} exists.")
            return True
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        return False

def main():
    print("Initializing database with Alembic migrations in Docker environment...")
    
    # Get environment variables
    pg_user = os.environ.get("POSTGRES_USER", "postgres")
    pg_password = os.environ.get("POSTGRES_PASSWORD", "psql")
    pg_database = os.environ.get("POSTGRES_DB", "postgres")
    pg_host = os.environ.get("POSTGRES_HOST", "localhost")
    pg_port = os.environ.get("POSTGRES_PORT", "5432")
    
    print(f"Using PostgreSQL at: {pg_host} with database: {pg_database}")
    
    # Connection string for default postgres database
    admin_connection_string = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/postgres"
    
    # Final connection string for application database
    connection_string = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    
    # Check PostgreSQL connection
    if not check_postgres_connection(admin_connection_string):
        print("Cannot connect to PostgreSQL. Make sure the container is running.")
        sys.exit(1)
    
    # Create database if it doesn't exist
    if not create_database_if_not_exists(admin_connection_string, pg_database):
        print("Failed to create or verify database.")
        sys.exit(1)
    
    # Update alembic.ini
    alembic_ini = "alembic.ini"
    if os.path.exists(alembic_ini):
        print("Checking alembic.ini configuration...")
        with open(alembic_ini, "r") as f:
            config = f.read()
        
        if "sqlalchemy.url = " in config:
            print("Updating database connection string in alembic.ini...")
            updated_config = ""
            for line in config.splitlines():
                if line.startswith("sqlalchemy.url = "):
                    updated_config += f"sqlalchemy.url = {connection_string}\n"
                else:
                    updated_config += line + "\n"
            
            with open(alembic_ini, "w") as f:
                f.write(updated_config)
    
    # Run alembic migrations
    print("Running alembic migrations...")
    try:
        run_command("alembic upgrade head")
        print("Database migrations completed successfully!")
    except Exception as e:
        print(f"Error running migrations: {e}")
        sys.exit(1)
    
    print("Database initialization complete!")

if __name__ == "__main__":
    main()