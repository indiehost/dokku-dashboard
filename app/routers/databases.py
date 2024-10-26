import logging

from dokku import dokku_commands
from fastapi import APIRouter
from models import DokkuDatabaseCreate, DokkuDatabaseLink

# ======================================================= Config
router = APIRouter()
logger = logging.getLogger(__name__)


# ======================================================= Routes
@router.post("")
async def create_database(database: DokkuDatabaseCreate):
    """
    Create a new Dokku database.
    """
    return await dokku_commands.create_database(database.plugin_name, database.database_name)


async def link_database(database: DokkuDatabaseLink):
    """
    Link a database to an app.
    """
    return await dokku_commands.link_database(database.plugin_name, database.database_name, database.app_name)
