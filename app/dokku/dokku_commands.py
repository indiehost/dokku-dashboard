import logging

from dokku import dokku_client, dokku_parser
from exceptions import DokkuCommandError, DokkuParseError
from models import DokkuResponse

# ======================================================= Config
logger = logging.getLogger(__name__)


# ======================================================= Commands
async def list_apps():
    command = "apps:list"
    parser_func = dokku_parser.parse_apps_list

    return await _execute_and_parse(command, parser_func)


async def list_app_domains(app_name: str):
    command = f"domains:report {app_name}"
    parser_func = dokku_parser.parse_domains_report

    return await _execute_and_parse(command, parser_func)


# ======================================================= Execute
async def _execute_and_parse(command: str, parser_func: callable):
    """
    Execute a Dokku command and parse its data.

    Args:
        command (str): The Dokku command to execute.
        parser_func (callable): The function to parse the command data.

    Returns:
        The parsed output of the command.

    Raises:
        DokkuCommandError: If the command execution fails.
        DokkuParseError: If the output parsing fails.
    """
    response = await dokku_client.execute(command)
    _validate_response(response)
    return _parse_output(response, command, parser_func)


def _validate_response(response: DokkuResponse):
    """
    Check the Dokku command response for errors.

    Args:
        response: The response from the Dokku command execution.

    Raises:
        DokkuCommandError: If the command execution fails.
        DokkuParseError: If the response format is unexpected.
    """
    # command execution failed
    if not response.success:
        raise DokkuCommandError(f"Dokku command failed: {response.error}")

    # command executed but returned unexpected output
    if not isinstance(response.data, dict) or response.data.get("output") is None:
        raise DokkuParseError(f"Unexpected response format: {response.data}")

    # command executed but failed
    if response.data.get("ok") is False:
        error_message = response.data.get("output") or response.data
        raise DokkuCommandError(f"Dokku command failed: {error_message}")


def _parse_output(response: DokkuResponse, command: str, parser_func: callable):
    """
    Parse the output of a Dokku command.

    Args:
        response: The response from the Dokku command execution.
        command (str): The original Dokku command.
        parser_func (callable): The function to parse the command output.

    Returns:
        The parsed output of the command.

    Raises:
        DokkuParseError: If the output parsing fails.
    """
    try:
        return parser_func(response.data.get("output"))  # dokku output is nested in "output" key
    except Exception as e:
        logger.error(f"Failed to parse Dokku output for command: {command}: {str(e)}")
        raise DokkuParseError(f"Failed to parse Dokku output for command: {command}: {str(e)}")
