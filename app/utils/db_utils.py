from models import GitHubAppCredentials
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


# ======================================================= Helpers
def health_check(db: Session):
    """
    Health check for the database
    """
    db.exec(text("SELECT 1"))
