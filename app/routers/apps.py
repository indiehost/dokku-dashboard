import logging

from database import get_session
from dokku import dokku_commands
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models import DeploymentConfig, DeploymentConfigCreate, DokkuAppCreate
from sqlmodel import Session
from utils import db_utils, github_utils

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
async def rebuild_app(app_name: str, background_tasks: BackgroundTasks):
    """
    Rebuild a Dokku app.
    """
    # run as background task as this can take a while
    background_tasks.add_task(dokku_commands.rebuild_app, app_name)
    return {"started": True}


@router.post("/{app_name}/start")
async def start_app(app_name: str):
    """
    Start a Dokku app.
    """
    return await dokku_commands.start_app(app_name)


@router.post("/{app_name}/stop")
async def stop_app(app_name: str):
    """
    Stop a Dokku app.
    """
    return await dokku_commands.stop_app(app_name)


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


# ======================================================= Deployment Config
@router.get("/{app_name}/deployment-config", response_model=DeploymentConfig)
async def get_app_deployment_config(app_name: str, db: Session = Depends(get_session)):
    """
    Get a Dokku app's deployment config.

    Temporary for testing git repo deployments, will change
    """
    return db_utils.get_deployment_config_by_app_name(db, app_name)


@router.post("/{app_name}/deployment-config")
async def create_deployment_config(
    deployment_config: DeploymentConfigCreate, db: Session = Depends(get_session), background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Create a deployment config for a Dokku app.

    Temporary for testing git repo deployments, will change
    """
    logger.info(f"Creating deployment config for app: {deployment_config.dokku_app_name}")

    # check if app already has a deployment config
    existing_deployment_config = db_utils.get_deployment_config_by_app_name(db, deployment_config.dokku_app_name)
    if existing_deployment_config:
        raise HTTPException(status_code=400, detail=f"Deployment config already exists for app: {deployment_config.dokku_app_name}")

    # save deployment config in db
    db_deployment_config = db_utils.create_deployment_config(db, deployment_config)
    logger.info(f"Saved deployment config to database for app: {deployment_config.dokku_app_name}")

    # get app credentials
    github_app_credentials = db_utils.get_github_app_credentials_by_app_id(db, deployment_config.github_app_id)
    if not github_app_credentials:
        raise HTTPException(status_code=404, detail=f"GitHub app credentials not found for app ID: {deployment_config.github_app_id}")

    logger.info(f"Retrieved GitHub app credentials for app ID: {deployment_config.github_app_id}")

    # get repo credentials
    client = github_utils.GitHubAppClient(github_app_credentials)
    access_token = client.get_installation_access_token(deployment_config.github_app_installation_id)
    logger.info(f"Retrieved installation access token for installation ID: {deployment_config.github_app_installation_id}")

    # set build directory if provided
    if deployment_config.build_directory:
        logger.info(f"Setting build directory to: {deployment_config.build_directory}")
        await dokku_commands.set_app_build_dir(deployment_config.dokku_app_name, deployment_config.build_directory)

    # Build GitHub URL with access token
    git_url_with_access_token = github_utils.build_github_url_with_access_token(deployment_config.github_repo_url, access_token)
    logger.info(f"Starting deployment from repository: {deployment_config.github_repo_url}")

    # trigger deployment as background task as it can take a while
    background_tasks.add_task(dokku_commands.sync_app_from_git_url, app_name=deployment_config.dokku_app_name, git_url=git_url_with_access_token)

    return db_deployment_config


# ======================================================= Helpers
