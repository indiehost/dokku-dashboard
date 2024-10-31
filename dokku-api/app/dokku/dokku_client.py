import asyncio
import contextlib
import json
import logging
import re
import socket

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
        # Create the Unix domain socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        logger.debug("Created Unix domain socket")

        # Set non-blocking mode for asyncio compatibility
        sock.setblocking(False)

        # Connect using asyncio
        loop = asyncio.get_running_loop()
        await loop.sock_connect(sock, SOCKET_PATH)
        logger.debug(f"Connected to dokku daemon at {SOCKET_PATH}")

        try:
            # Send the command with a newline
            command_bytes = f"{command}\n".encode("utf-8")
            await loop.sock_sendall(sock, command_bytes)
            logger.debug("Sent command to dokku daemon")

            # Read the response
            response_data = bytearray()

            # TODO some commands dont need to read response, add option to skip

            async def read_response():
                while True:
                    chunk = await loop.sock_recv(sock, 4096)
                    if not chunk:
                        break
                    response_data.extend(chunk)

                # Move the JSON parsing outside the loop to ensure we have the complete response
                try:
                    response_str = response_data.decode("utf-8").strip()
                    # Remove ANSI escape codes
                    # TODO: dokku should have format flag to avoid this
                    ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
                    response_str_clean = ansi_escape.sub("", response_str)
                    return json.loads(response_str_clean)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.error("JSON Decode Error")
                    return response_str_clean

            # Use asyncio.wait_for to implement timeout
            response_json = await asyncio.wait_for(read_response(), timeout=timeout)
            logger.info("Received response from dokku daemon")

            return DokkuResponse(success=True, data=response_json)

        finally:
            # Ensure socket is properly closed
            with contextlib.suppress(Exception):
                sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            logger.debug("Closed connection to dokku daemon")

    except asyncio.TimeoutError:
        logger.error(f"Command timed out after {timeout} seconds")
        return DokkuResponse(success=False, error=f"Command timed out after {timeout} seconds")
    except (ConnectionRefusedError, FileNotFoundError):
        logger.error(f"Could not connect to dokku daemon at {SOCKET_PATH}")
        return DokkuResponse(success=False, error=f"Could not connect to dokku daemon at {SOCKET_PATH}")
    except json.JSONDecodeError:
        logger.error("Invalid JSON response from dokku daemon")
        return DokkuResponse(success=False, error="Invalid JSON response from dokku daemon")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return DokkuResponse(success=False, error=f"Unexpected error: {str(e)}")
