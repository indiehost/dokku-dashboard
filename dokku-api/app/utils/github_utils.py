import hashlib
import hmac
import json
import logging

from dotenv import load_dotenv
from fastapi import HTTPException, Request, Response
from github import Auth, GithubIntegration
from models import GitHubAppCredentials
from sqlmodel import Session
from utils import db_utils

# ======================================================= Config
logger = logging.getLogger(__name__)

load_dotenv()


# ======================================================= PyGithub client
class GitHubAppClient:
    def __init__(self, credentials: GitHubAppCredentials):
        self.auth = Auth.AppAuth(credentials.app_id, credentials.private_key_encrypted)
        self.integration = GithubIntegration(auth=self.auth, per_page=100)

    def get_installations(self):
        """Get all installations of the GitHub App"""
        return self.integration.get_installations()

    def get_installation_access_token(self, installation_id):
        """Get Github instance for a specific installation"""
        return self.integration.get_access_token(installation_id).token


# ======================================================= Webhooks
async def handle_push_event(payload: dict, credentials: GitHubAppCredentials):
    """
    Handle push events from GitHub
    """
    client = GitHubAppClient(credentials)
    installation_id = payload["installation"]["id"]

    try:
        access_token = client.get_installation_access_token(installation_id)
        logger.info(f"Access token: {access_token}")
    except Exception as e:
        logger.error(f"Error handling push event: {str(e)}")
        return Response(status_code=500)

    return Response(status_code=200)


async def verify_signature(request: Request, credentials: GitHubAppCredentials):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    payload_body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256")

    # Ensure signature header is present
    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing !")

    # Decrypt the webhook secret
    webhook_secret = credentials.webhook_secret_encrypted  # TODO: decrypt here once implemented

    # Create expected signature
    hash_object = hmac.new(webhook_secret.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()

    # Compare signatures
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


# ======================================================= App creation manifest
def create_app_manifest(dokku_api_url: str, webhook_url: str, callback_url: str):
    """
    Create the GitHub App manifest
    """
    # Define the GitHub App manifest
    manifest = {
        "name": f"indiehost-server",  # Make name unique
        "url": dokku_api_url,
        "hook_attributes": {
            "url": webhook_url,
        },
        "redirect_url": callback_url,  # This is where GitHub will redirect to after the app is created
        # "callback_urls": [callback_url],  # List of valid callback URLs after someone authorizes the app
        "public": True,
        "default_permissions": {
            "contents": "read",
            "metadata": "read",
            "deployments": "write",
            "pull_requests": "write",
        },
        "default_events": ["push", "pull_request"],
    }

    return json.dumps(manifest)


# ======================================================= Credentials
def save_github_app_credentials(db: Session, app_data: dict):
    """
    Save the GitHub App credentials to the database
    """
    credentials = GitHubAppCredentials(
        app_id=app_data["id"],
        app_name=app_data["name"],
        client_id=app_data["client_id"],
        client_secret_encrypted=app_data["client_secret"],  # TODO: encrypt before storing
        private_key_encrypted=app_data["pem"],  # TODO: encrypt before storing
        webhook_secret_encrypted=app_data["webhook_secret"],  # TODO: encrypt before storing
    )

    logger.info(f"Saving GitHub App credentials for app id: {credentials.app_id}")
    db_utils.save_github_app_credentials(db, credentials)


def build_github_url_with_access_token(repo_url: str, access_token: str) -> str:
    """
    Convert a GitHub HTTPS URL to include an access token.
    Example:
    Input: https://github.com/owner/repo.git, token123
    Output: https://token:token123@github.com/owner/repo.git
    """
    # Remove https:// if present
    clean_url = repo_url.replace("https://", "")
    return f"https://token:{access_token}@{clean_url}"
