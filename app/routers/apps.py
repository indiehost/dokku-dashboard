import logging

from dokku import dokku_commands
from fastapi import APIRouter

# ======================================================= Config
router = APIRouter()
logger = logging.getLogger(__name__)


# ======================================================= Routes
@router.get("")
async def get_apps():
    """
    List all dokku apps.
    """
    return await dokku_commands.list_apps()


@router.get("/{app_name}/domains")
async def get_app_domains(app_name: str):
    """
    List all domains for a given app.
    """
    return await dokku_commands.list_app_domains(app_name)
