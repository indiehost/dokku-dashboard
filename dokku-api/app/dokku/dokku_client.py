import asyncio
import json
import logging
import re

from models import DokkuResponse

# ======================================================= Config
logger = logging.getLogger(__name__)

# Dokku daemon socket path
SOCKET_PATH = "/var/run/dokku-daemon/dokku-daemon.sock"


# ============================================================= Logic
async def execute(command: str, timeout: float = 60.0) -> DokkuResponse:
    """
    Send a command to the dokku-daemon socket using asyncio.

    Args:
        command (str): The command to send to the dokku-daemon.
        timeout (float): The maximum time to wait for response
    """
    logger.info(f"Executing dokku command: {command}")
    try:
        reader, writer = await asyncio.open_unix_connection(SOCKET_PATH)
        logger.debug(f"Connected to dokku daemon at {SOCKET_PATH}")

        try:
            # Send the command with a newline
            writer.write(f"{command}\n".encode("utf-8"))
            await writer.drain()
            logger.debug("Sent command to dokku daemon")

            # Read response directly
            response_data = await asyncio.wait_for(reader.readline(), timeout=timeout)
            response_json = parse_dokku_response(response_data)
            logger.info("Received response from dokku daemon")

            return DokkuResponse(success=True, data=response_json)

        finally:
            writer.close()
            await writer.wait_closed()
            logger.debug("Closed connection to dokku daemon")

    except asyncio.TimeoutError:
        logger.error(f"Command timed out after {timeout} seconds")
        return DokkuResponse(success=False, error=f"Command timed out after {timeout} seconds")
    except (ConnectionRefusedError, FileNotFoundError):
        logger.error(f"Could not connect to dokku daemon at {SOCKET_PATH}")
        return DokkuResponse(success=False, error=f"Could not connect to dokku daemon at {SOCKET_PATH}")
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error("Invalid JSON response from dokku daemon")
        return DokkuResponse(success=False, error="Invalid JSON response from dokku daemon")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return DokkuResponse(success=False, error=f"Unexpected error: {str(e)}")


def parse_dokku_response(raw_data: bytes) -> dict:
    """Parse the raw dokku response, handling ANSI codes and JSON decoding."""
    response_str = raw_data.decode("utf-8").strip()
    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    response_str_clean = ansi_escape.sub("", response_str)
    return json.loads(response_str_clean)
