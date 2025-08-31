# app/db/database.py
import os
import logging
from dotenv import load_dotenv
import sqlalchemy
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# -------------------------
# Environment variables
# -------------------------
DB_HOST = os.getenv("DB_HOST", "0.0.0.0")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "your_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_NAME = os.getenv("DB_NAME", "your_db")

# -------------------------
# Global objects
# -------------------------
_sync_engine = None
_async_pool = None

# -------------------------
# Synchronous SQLAlchemy
# -------------------------
def get_sync_engine():
    global _sync_engine
    if _sync_engine is None:
        _sync_engine = sqlalchemy.create_engine(
            f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
            pool_size=5,
            max_overflow=0,
            pool_timeout=30,
            pool_recycle=1800,
        )
        logger.info("Synchronous SQLAlchemy engine created")
    return _sync_engine

# -------------------------
# Asynchronous asyncpg pool
# -------------------------
async def init_async_pool():
    """Initialize asyncpg pool if not exists"""
    global _async_pool
    if _async_pool is None:
        _async_pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            min_size=1,
            max_size=10
        )
        logger.info("Asyncpg pool created successfully")
    return _async_pool

async def close_async_pool():
    global _async_pool
    if _async_pool:
        await _async_pool.close()
        _async_pool = None
        logger.info("Asyncpg pool closed")

# Dependency for FastAPI to get a database connection from the pool
async def get_db():
    """Dependency to provide a database connection from the pool."""
    global _async_pool
    if _async_pool is None:
        raise RuntimeError("Database pool is not initialized. Call init_async_pool() first.")
    conn = await _async_pool.acquire()
    try:
        yield conn
    finally:
        await _async_pool.release(conn)
            
def get_async_pool():
    """Getter for the async pool (always reference latest)"""
    if _async_pool is None:
        raise RuntimeError("Async pool is not initialized")
    return _async_pool
