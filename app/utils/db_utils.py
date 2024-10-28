from models import DeploymentConfig, DeploymentConfigCreate, GitHubAppCredentials
from sqlalchemy import text
from sqlmodel import select, Session


# ======================================================= GitHub Credentials
def get_all_github_app_credentials(db: Session):
    """
    Get all GitHub App credentials
    """
    return db.exec(select(GitHubAppCredentials)).all()


def get_github_app_credentials_by_app_id(db: Session, app_id: str):
    """
    Get the GitHub App credentials for a given app ID
    """
    return db.exec(select(GitHubAppCredentials).where(GitHubAppCredentials.app_id == app_id)).first()


def save_github_app_credentials(db: Session, credentials: GitHubAppCredentials):
    """
    Save the GitHub App credentials to the database
    """
    db.add(credentials)
    db.commit()


# ======================================================= Deployments
def get_deployment_config_by_app_name(db: Session, app_name: str):
    """
    Get a deployment config by app name
    """
    return db.exec(select(DeploymentConfig).where(DeploymentConfig.dokku_app_name == app_name)).first()


def create_deployment_config(db: Session, deployment_config: DeploymentConfigCreate):
    """
    Create a deployment config
    """
    deployment_config = DeploymentConfig.model_validate(deployment_config)
    db.add(deployment_config)
    db.commit()


# ======================================================= Helpers
def health_check(db: Session):
    """
    Health check for the database
    """
    db.exec(text("SELECT 1"))
