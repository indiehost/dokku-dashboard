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


@router.post("/{app_name}/restart")
async def restart_app(app_name: str):
    """
    Restart a Dokku app.
    """
    return await dokku_commands.restart_app(app_name)


@router.post("/{app_name}/rebuild")
async def rebuild_app(app_name: str):
    """
    Rebuild a Dokku app.
    """
    return await dokku_commands.rebuild_app(app_name)


@router.delete("/{app_name}")
async def delete_app(app_name: str):
    """
    Permanently delete a Dokku app.
    """
    return await dokku_commands.destroy_app(app_name)


@router.get("/{app_name}/domains")
async def get_app_domains_report(app_name: str):
    """
    List all domains for a given app.
    """
    return await dokku_commands.app_domains_report(app_name)
