import logging

from dokku import dokku_commands
from fastapi import APIRouter
from models import DokkuAppCreate

# ======================================================= Config
router = APIRouter()
logger = logging.getLogger(__name__)


# ======================================================= Routes
@router.get("")
async def list_apps():
    """
    List all dokku apps.
    """
    return await dokku_commands.list_apps()


@router.post("")
async def create_app(app: DokkuAppCreate):
    """
    Create a new Dokku app.
    """
    return await dokku_commands.create_app(app.name)


@router.get("/{app_name}/domains")
async def get_app_domains_report(app_name: str):
    """
    List all domains for a given app.
    """
    return await dokku_commands.app_domains_report(app_name)
