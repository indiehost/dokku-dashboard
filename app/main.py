import logging
from fastapi import FastAPI
from database import initialize_database
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# ======================================================= Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)-9s [%(name)-8s] %(message)s")
logger = logging.getLogger(__name__)

# ======================================================= Lifecycle events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecylce events for the FastAPI application.
    Lines before 'yield' are executed at startup, lines after during shutdown
    """
    await startup()
    yield
    await shutdown()

async def startup():
    """
    Startup tasks
    """
    try:
        await initialize_database()
    except:
        logger.error("Failed to initialize DB and scheduler")

async def shutdown():
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
# app.include_router(servers.router, prefix="/servers")

# ======================================================= Routes
@app.get("/")
async def root():
    """
    Return a hello world message.
    """
    logger.info("Root endpoint accessed")
    return {"message": "Hello world"}
