import logging
import os
from contextlib import asynccontextmanager

from database import get_session, initialize_database
from dokku import dokku_client
from exceptions import (
    dokku_command_exception_handler,
    dokku_parse_exception_handler,
    dokku_plugin_not_supported_exception_handler,
    DokkuCommandError,
    DokkuParseError,
    DokkuPluginNotSupportedError,
    generic_exception_handler,
)
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import DokkuCommandRequest
from routers import apps, github
from sqlmodel import Session
from utils.db_utils import create_test, delete_test

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
    logger.info("Health check endpoint accessed")

    # test db entry to see that connection is working
    db_test = create_test(db, "test", "test")
    delete_test(db, db_test.id)
    return db_test


@app.post("/dokku/command")
async def execute_command(request: DokkuCommandRequest):
    """
    Execute a dokku command.
    """
    response = await dokku_client.execute(request.command)
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    return response.data
