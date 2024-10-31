import logging

from dokku import dokku_commands
from fastapi import APIRouter

# ======================================================= Config
router = APIRouter()
logger = logging.getLogger(__name__)


# ======================================================= Routes
@router.get("/{app_name}")
async def get_app(app_name: str):
    """
    Get logs for a Dokku app.
    """
    return await dokku_commands.get_app_logs(app_name)
