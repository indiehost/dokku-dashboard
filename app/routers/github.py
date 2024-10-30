import logging
import os
import secrets

import requests
from database import get_session
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel import Session
from utils import db_utils, github_utils

# ======================================================= Config
router = APIRouter()
logger = logging.getLogger(__name__)

load_dotenv()

DOKKU_API_URL = os.getenv("DOKKU_API_URL", "http://localhost:8000")
GITHUB_WEBHOOK_URL = f"{DOKKU_API_URL}/github/webhook"
GITHUB_APP_CALLBACK_URL = f"{DOKKU_API_URL}/github/apps/create/callback"


# ======================================================= GitHub app
@router.get("/installations")
async def list_installations(db: Session = Depends(get_session)):
    """
    List all installations and repositories for the GitHub App, organized by app and installation.
    Returns a structured list of apps, their installations, and available repositories.
    """
    # TODO: Break into smaller chunks, no need to get all this data at once
    apps_list = []
    credentials = db_utils.get_all_github_app_credentials(db)

    for credential in credentials:
        logger.info(f"Getting installations for GitHub App ID: {credential.app_id}")
        app_data = {"app_id": credential.app_id, "app_name": credential.app_name, "installations": []}

        client = github_utils.GitHubAppClient(credential)

        logger.info(f"Getting installations for GitHub App with ID: {credential.app_id}")
        installations = client.get_installations()

        for installation in installations:
            installation_data = {
                "id": installation.raw_data["id"],
                "account_name": installation.raw_data["account"]["login"],
                "account_type": installation.raw_data["account"]["type"],  # Will be either "User" or "Organization"
                "account_avatar": installation.raw_data["account"]["avatar_url"],
                "repositories": [],
            }

            # Get repositories for each installation
            repos = installation.get_repos()
            for repo in repos:
                repo_data = {
                    "id": repo.id,
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "private": repo.private,
                    "html_url": repo.html_url,
                    "git_url": repo.url,
                }
                installation_data["repositories"].append(repo_data)

            app_data["installations"].append(installation_data)

        apps_list.append(app_data)

    return apps_list


@router.post("/apps/create")
async def create_github_app():
    """
    Creates a new GitHub App in the users account using the manifest flow.
    """
    logger.info("Starting GitHub App manifest flow")

    # Generate state param for CSRF
    state = secrets.token_hex(16)
    manifest = github_utils.create_app_manifest(DOKKU_API_URL, GITHUB_WEBHOOK_URL, GITHUB_APP_CALLBACK_URL)

    # Construct the GitHub App creation URL
    github_url = f"https://github.com/settings/apps/new?state={state}&manifest={manifest}"

    # Redirect to GitHub's manifest flow to create the app
    logger.info(f"Redirecting to GitHub App creation URL")
    return RedirectResponse(github_url)


@router.get("/apps/create/callback")
def handle_create_callback(code: str, db: Session = Depends(get_session)):
    """
    Handle the callback from GitHub's App manifest flow
    """
    logger.info(f"Received GitHub App manifest callback with code: {code}")

    # Exchange the temporary code for the app's credentials
    response = requests.post(f"https://api.github.com/app-manifests/{code}/conversions", headers={"Accept": "application/vnd.github.v3+json"})

    # Check if the response is successful
    if response.status_code != 201:
        logger.error(f"Failed to create GitHub App. Status code: {response.status_code}, Response: {response.text}")
        return JSONResponse(status_code=400, content={"error": "Failed to create GitHub App"})

    # Save app credentials in the database
    app_data = response.json()
    github_utils.save_github_app_credentials(db, app_data)

    logger.info(f"Successfully created GitHub App with ID: {app_data['id']}")

    # Redirect to app installation page
    logger.info(f"Redirecting to GitHub app installation page")
    redirect_url = f"https://github.com/apps/{app_data['slug']}/installations/new"
    return RedirectResponse(redirect_url)


# ======================================================= Webhook
@router.post("/webhook")
async def handle_github_webhook(request: Request, db: Session = Depends(get_session)):
    """
    Handle incoming webhooks from GitHub
    """
    # Get event type and payload
    event_type = request.headers.get("X-GitHub-Event")
    app_id = request.headers.get("X-GitHub-Hook-Installation-Target-ID")

    logger.info(f"Received GitHub webhook with event type: {event_type}, app ID: {app_id}")

    # Get corresponding GitHub App credentials from db
    credentials = db_utils.get_github_app_credentials_by_app_id(db, app_id)

    # Verify the webhook signature
    await github_utils.verify_signature(request, credentials)
    logger.info(f"Webhook signature verified for app ID: {app_id}")

    # Read the payload
    payload = await request.json()

    # Handle the events
    if event_type == "push":
        return await github_utils.handle_push_event(payload, credentials)

    # success
    return Response(status_code=200)
