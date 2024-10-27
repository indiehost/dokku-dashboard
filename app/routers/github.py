import hashlib
import hmac
import json
import logging
import os
import secrets
import time

import jwt
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse

# ======================================================= Config
router = APIRouter()
logger = logging.getLogger(__name__)

load_dotenv()

# This would come from your config
CALLBACK_URL = "http://localhost:8000/github/setup/callback"

# Add this constant at the top of your file with other constants
GITHUB_API_URL = "https://api.github.com"
GITHUB_APP_NAME = "indiehost-tester-1"  # Replace with your actual GitHub App name
GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY = os.environ.get("GITHUB_PRIVATE_KEY")
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET")


# ======================================================= Events
async def handle_push_event(payload: dict):
    """
    Handle push events from GitHub
    """
    logger.info(f"Received push event: {json.dumps(payload, indent=2)}")

    installation_id = payload["installation"]["id"]

    try:
        access_token = await get_installation_access_token(installation_id)
        logger.info(f"Access token: {access_token}")

        # TODO: trigger build if changes are in specified directory (always build if none specified)

    except Exception as e:
        logger.error(f"Error handling push event: {str(e)}")
        return Response(status_code=500)

    return Response(status_code=200)


async def verify_signature(request: Request):
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

    # Create expected signature
    hash_object = hmac.new(GITHUB_WEBHOOK_SECRET.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()

    # Compare signatures
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")


# ======================================================= Webhook
@router.post("/webhook")
async def handle_github_webhook(request: Request):
    """
    Handle incoming webhooks from GitHub
    """
    # Verify the webhook signature
    await verify_signature(request)

    # Get event type and payload
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    # Handle the different event types
    if event_type == "push":
        return await handle_push_event(payload)

    # success
    return Response(status_code=200)


# ======================================================= Create app in user's account
@router.post("/create")
async def create_github_app(request: Request):
    """
    Creates a new GitHub App in the users account using the manifest flow.
    """
    logger.info("Starting GitHub App manifest flow")
    # Generate a state parameter for security
    state = secrets.token_hex(16)
    logger.debug(f"Generated state: {state}")

    # Define the GitHub App manifest
    manifest = {
        "name": f"indiehost-server-name",  # Make name unique
        "url": "https://example.com",
        "hook_attributes": {
            "url": "https://example.com/api/webhook",
        },
        "redirect_url": CALLBACK_URL,
        "callback_urls": [CALLBACK_URL],
        "public": False,
        "default_permissions": {
            "contents": "read",
            "metadata": "read",
            "deployments": "write",
            "pull_requests": "write",
        },
        "default_events": ["push", "pull_request"],
    }

    # Encode the manifest as a JSON string
    manifest_json = json.dumps(manifest)
    logger.debug(f"Created manifest: {manifest_json}")

    # Construct the GitHub App creation URL
    github_url = f"https://github.com/settings/apps/new?state={state}&manifest={manifest_json}"
    logger.info(f"Redirecting to GitHub App creation URL: {github_url}")

    # Redirect to GitHub's manifest flow
    return RedirectResponse(github_url)


@router.get("/create/callback")
def handle_create_callback(code: str, state: str):
    """
    Handle the callback from GitHub's App manifest flow
    """
    logger.info(f"Received callback with code: {code} and state: {state}")

    # Exchange the temporary code for the app's credentials
    response = requests.post(f"https://api.github.com/app-manifests/{code}/conversions", headers={"Accept": "application/vnd.github.v3+json"})

    if response.status_code != 201:
        logger.error(f"Failed to create GitHub App. Status code: {response.status_code}, Response: {response.text}")
        return JSONResponse(status_code=400, content={"error": "Failed to create GitHub App"})

    app_data = response.json()
    logger.info(f"Successfully created GitHub App with ID: {app_data['id']}")

    # Store these securely in your database
    credentials = {
        "id": app_data["id"],
        "slug": app_data["slug"],
        "pem": app_data["pem"],  # This is the private key
        "webhook_secret": app_data["webhook_secret"],
        "client_id": app_data["client_id"],
        "client_secret": app_data["client_secret"],
    }

    logger.info("Credentials extracted from app_data")
    logger.debug(f"Credentials: {credentials}")
    # Here you would save the credentials to your database
    # logger.info("Credentials saved to database")  # Uncomment when implemented

    # Redirect to your app's setup completion page
    redirect_url = f"http://localhost:8000/setup/complete?app_id={app_data['id']}"
    logger.info(f"Redirecting to setup completion page: {redirect_url}")
    return RedirectResponse(redirect_url)


async def get_installation_access_token(installation_id: int) -> str:
    """
    Get an installation access token for a given installation ID.
    """
    # Convert the string newlines (\n) to actual newlines
    private_key = GITHUB_PRIVATE_KEY.replace("\\n", "\n")

    now = int(time.time())
    payload = {"iat": now, "exp": now + 600, "iss": GITHUB_APP_ID}  # 10 minute expiration

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}

    response = requests.post(f"{GITHUB_API_URL}/app/installations/{installation_id}/access_tokens", headers=headers)

    if response.status_code != 201:
        logger.error(f"Failed to get github installation access token. Status code: {response.status_code}, Response: {response.text}")
        raise HTTPException(status_code=500, detail="Failed to get github installation access token")

    return response.json()["token"]
