import logging
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from dotenv import load_dotenv
from ksuid import Ksuid

# ======================================================= Config
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize database engine
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)

# ============================================================= Database setup
async def initialize_database():
    """
    Initialize the database using SQLModel.
    Creates all tables if they don't exist.
    """
    try:
        logger.info("Initializing database")
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")

async def get_async_session() -> AsyncIterator[AsyncSession]:
    """
    Dependency function to get an async database session.
    
    Yields:
        AsyncSession: An async SQLAlchemy session for database operations.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


def generate_id(prefix: str = "") -> str:
    """
    Generates a unique K-sorted id with the provided prefix to be used as a primary key.
    See: https://github.com/svix/python-ksuid
    """
    ksuid = Ksuid()

    # return plain ksuid if prefix not provided
    if (prefix == ""):
        return str(ksuid)
    
    return f"{prefix}_{ksuid}"
