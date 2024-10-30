import logging
import os

from dotenv import load_dotenv
from ksuid import Ksuid
from sqlmodel import create_engine, Session, SQLModel

# ======================================================= Config
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define the SQLite database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///dokku-api.db")

# Create the database engine
engine = create_engine(DATABASE_URL)


# ============================================================= Database setup
def initialize_database():
    """
    Initialize the database using SQLModel.
    Creates all tables if they don't exist.
    """
    try:
        logger.info("Initializing sqlite database")
        SQLModel.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")


def get_session():
    """
    Get a session for the database.
    """
    with Session(engine) as session:
        yield session


def generate_id(prefix: str = "") -> str:
    """
    Generates a unique K-sorted id with the provided prefix to be used as a primary key.
    See: https://github.com/svix/python-ksuid
    """
    ksuid = Ksuid()

    # return plain ksuid if prefix not provided
    if prefix == "":
        return str(ksuid)

    return f"{prefix}_{ksuid}"
