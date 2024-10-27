import hashlib
import hmac
import json
import logging
import os
import time

import jwt
import requests
from dotenv import load_dotenv
from fastapi import HTTPException, Request, Response
from models import GitHubAppCredentials
from sqlmodel import Session
from utils import db_utils

# ======================================================= Config
logger = logging.getLogger(__name__)

load_dotenv()

DOKKU_API_URL = os.getenv("DOKKU_API_URL")


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


async def get_access_token(installation_id: int, credentials: GitHubAppCredentials) -> str:
    """
    Get access token for a given installation ID.
    """
    # TODO: decrypt key here once implemented
    private_key_decrypted = credentials.private_key_encrypted

    # build jwt
    now = int(time.time())
    payload = {"iat": now, "exp": now + 600, "iss": credentials.app_id}  # 10 minute expiration
    encoded_jwt = jwt.encode(payload, private_key_decrypted, algorithm="RS256")
    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    # get access token and ensure success
    response = requests.post(f"https://api.github.com/app/installations/{installation_id}/access_tokens", headers=headers)
    if response.status_code != 201:
        logger.error(f"Failed to get github installation access token. Status code: {response.status_code}, Response: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to get github installation access token")

    return response.json()["token"]


# ======================================================= Webhooks
async def handle_push_event(payload: dict, credentials: GitHubAppCredentials):
    """
    Handle push events from GitHub
    """
    installation_id = payload["installation"]["id"]

    try:
        access_token = await get_access_token(installation_id, credentials)
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


# ======================================================= App creation
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
