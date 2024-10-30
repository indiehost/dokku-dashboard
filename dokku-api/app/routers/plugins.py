import logging

from dokku import dokku_commands
from fastapi import APIRouter
from models import DokkuPluginInstall

# ======================================================= Config
router = APIRouter()
logger = logging.getLogger(__name__)


# ======================================================= Routes
@router.get("")
async def list_plugins():
    """
    List all dokku plugins.
    """
    return await dokku_commands.list_plugins()


@router.post("")
async def install_plugin(plugin: DokkuPluginInstall):
    """
    Install a new Dokku plugin.
    """
    return await dokku_commands.install_plugin(plugin.name)
