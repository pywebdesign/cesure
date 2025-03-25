#!/usr/bin/env python3
"""
Docker-compatible reset database script: drops and recreates the database, then runs migrations
"""

import os
import subprocess
import sys

def run_command(command, check=True):
    """Run a shell command and return its output."""
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

def main():
    # Get environment variables
    pg_user = os.environ.get("POSTGRES_USER", "postgres")
    pg_database = os.environ.get("POSTGRES_DB", "postgres")
    pg_host = os.environ.get("POSTGRES_HOST", "postgres")
    
    # Support skipping confirmation with environment variable
    if os.environ.get("SKIP_CONFIRMATION") != "true":
        confirm = input(f"This will DROP and RECREATE the database '{pg_database}'. All data will be lost! Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    print(f"Dropping database {pg_database}...")
    
    # Terminate all connections
    run_command(f"psql -h {pg_host} -U {pg_user} -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{pg_database}'\"", check=False)
    
    # Drop and recreate database
    run_command(f"dropdb -h {pg_host} -U {pg_user} {pg_database}", check=False)
    run_command(f"createdb -h {pg_host} -U {pg_user} {pg_database}")
    
    print("Database recreated. Running migrations...")
    
    # Run alembic migrations
    run_command("alembic upgrade head")
    
    print("Database reset complete!")

if __name__ == "__main__":
    main()