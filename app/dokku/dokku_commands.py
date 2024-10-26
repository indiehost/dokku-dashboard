import logging

from dokku import dokku_client, dokku_parser
from exceptions import DokkuCommandError, DokkuParseError, DokkuPluginNotSupportedError
from models import DokkuResponse

# ======================================================= Config
logger = logging.getLogger(__name__)

SUPPORTED_DATABASE_PLUGINS = ["postgres", "mysql"]


# ======================================================= Apps
async def list_apps():
    """
    List all Dokku apps.
    """
    command = "apps:list"
    parser_func = dokku_parser.parse_apps_list

    return await _execute_and_parse(command, parser_func)


async def create_app(app_name: str):
    """
    Create a new Dokku app.
    """
    command = f"apps:create {app_name}"

    return await _execute_and_parse(command, parser_func=None)


async def app_domains_report(app_name: str):
    """
    Get a report on the domains for a given app.
    """
    command = f"domains:report {app_name}"
    parser_func = dokku_parser.parse_domains_report

    return await _execute_and_parse(command, parser_func)


# ======================================================= Plugins
async def list_plugins():
    """
    List all Dokku plugins.
    """
    command = "plugin:list"

    return await _execute_and_parse(command, parser_func=None)


async def install_plugin(plugin_name: str):
    """
    Install a new Dokku plugin.
    """
    if plugin_name == "postgres":
        command = "plugin:install https://github.com/dokku/dokku-postgres.git"
    elif plugin_name == "mysql":
        command = "plugin:install https://github.com/dokku/dokku-mysql.git mysql"
    else:
        raise DokkuPluginNotSupportedError(f"Plugin not found: {plugin_name}")

    return await _execute_and_parse(command, parser_func=None)


# ======================================================= Databases
async def create_database(plugin_name: str, database_name: str):
    """
    Create a new Dokku database.
    """
    _ensure_database_supported(plugin_name)
    command = f"{plugin_name}:create {database_name}"

    return await _execute_and_parse(command, parser_func=None)


async def link_database(plugin_name: str, database_name: str, app_name: str):
    """
    Link a database to an app.
    """
    _ensure_database_supported(plugin_name)
    command = f"{plugin_name}:link {database_name} {app_name}"

    return await _execute_and_parse(command, parser_func=None)


# ======================================================= Execution
async def _execute_and_parse(command: str, parser_func: callable = None):
    """
    Execute a Dokku command and optionally parse its data.

    Args:
        command (str): The Dokku command to execute.
        parser_func (callable, optional): The function to parse the command data.

    Returns:
        The parsed output of the command or the raw output if no parser is provided.

    Raises:
        DokkuCommandError: If the command execution fails.
        DokkuParseError: If the output parsing fails.
    """
    response = await dokku_client.execute(command)
    _validate_response(response)

    if parser_func is None:
        return response.data.get("output")

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
        raise DokkuCommandError(response.error)

    # command executed but returned unexpected output
    if not isinstance(response.data, dict) or response.data.get("output") is None:
        raise DokkuParseError(f"Unexpected response format: {response.data}")

    # command executed but failed
    if response.data.get("ok") is False:
        error_message = response.data.get("output") or response.data
        raise DokkuCommandError(error_message)


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


# ======================================================= Helpers
def _ensure_database_supported(plugin_name: str):
    """
    Ensure the database plugin is supported.
    """
    if plugin_name not in SUPPORTED_DATABASE_PLUGINS:
        raise DokkuPluginNotSupportedError(f"Plugin not found: {plugin_name}")
