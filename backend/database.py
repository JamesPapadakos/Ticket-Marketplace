import os

import psycopg
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()


def get_connection():
    """Create a connection to PostgreSQL."""
    try:
        return psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    except psycopg.OperationalError:
        raise HTTPException(
            status_code=503,
            detail="Database connection unavailable",
        )