import logging
import os
from contextlib import asynccontextmanager

from database import get_session, initialize_database
from dokku import dokku_client, dokku_commands
from exceptions import (
    dokku_command_exception_handler,
    dokku_parse_exception_handler,
    dokku_plugin_not_supported_exception_handler,
    DokkuCommandError,
    DokkuParseError,
    DokkuPluginNotSupportedError,
    generic_exception_handler,
)
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import DokkuCommandRequest
from routers import apps, github, logs
from sqlmodel import Session
from utils import db_utils

# ======================================================= Logging setup
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(levelname)-9s [%(name)-8s] %(message)s")
logger = logging.getLogger(__name__)


# ======================================================= Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecylce events for the FastAPI application.
    Lines before 'yield' are executed at startup, lines after during shutdown
    """
    startup()
    yield
    shutdown()


def startup():
    """
    Startup tasks
    """
    initialize_database()


def shutdown():
    """
    Shutdown tasks
    """
    return


# ======================================================= Root FastAPI application
app = FastAPI(lifespan=lifespan)

# ======================================================= CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ======================================================= Routers
app.include_router(apps.router, prefix="/apps")
app.include_router(github.router, prefix="/github")
app.include_router(logs.router, prefix="/logs")

# ======================================================= Exception handlers
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(DokkuCommandError, dokku_command_exception_handler)
app.add_exception_handler(DokkuParseError, dokku_parse_exception_handler)
app.add_exception_handler(DokkuPluginNotSupportedError, dokku_plugin_not_supported_exception_handler)


# ======================================================= Routes
@app.get("/")
async def root():
    """
    Return a hello world message.
    """
    logger.info("Root endpoint accessed")
    return {"message": "Hello world"}


@app.get("/health")
async def health_check(db: Session = Depends(get_session)):
    """
    Health check endpoint
    """
    try:
        db_utils.health_check(db)  # check db connection
        await dokku_commands.list_apps()  # check dokku connection

        return {"status": "healthy", "database": "connected", "dokku": "connected", "version": "0.0.7"}  # manually incrementing this for now, hacky
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Database connection failed")


@app.post("/update")
async def update(background_tasks: BackgroundTasks):
    """
    Update Dokku API to latest version.
    """
    # run as background task as this can take a while
    background_tasks.add_task(dokku_commands.sync_app_from_git_url, app_name="dokku-api", git_url="https://github.com/indiehost/dokku-dashboard.git")
    return {"status": "started"}


@app.post("/dokku/command")
async def execute_command(request: DokkuCommandRequest):
    """
    Execute a dokku command.
    """
    response = await dokku_client.execute(request.command)
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    return response.data
