from models import GitHubAppCredentials
from sqlalchemy import text
from sqlmodel import select, Session


def health_check(db: Session):
    """
    Health check for the database
    """
    db.exec(text("SELECT 1"))


def get_github_app_credentials(db: Session, app_id: str):
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
