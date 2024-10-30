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
    return await _execute(command, parser_func)


async def get_app_report(app_name: str):
    """
    Get a Dokku app report.
    """
    command = f"apps:report {app_name}"
    parser_func = dokku_parser.parse_report
    return await _execute(command, parser_func)


async def create_app(app_name: str):
    """
    Create a new Dokku app.
    """
    command = f"apps:create {app_name}"
    return await _execute(command)


async def restart_app(app_name: str):
    """
    Restart a Dokku app.
    """
    command = f"ps:restart {app_name}"
    return await _execute(command)


async def rebuild_app(app_name: str):
    """
    Rebuild a Dokku app.

    NOTE: This command can take a long time to complete. Best run as a background task.
    """
    command = f"ps:rebuild {app_name}"
    return await _execute(command, timeout=600.0)  # 10 minute timeout for builds


async def start_app(app_name: str):
    """
    Start a Dokku app.
    """
    command = f"ps:start {app_name}"
    return await _execute(command)


async def stop_app(app_name: str):
    """
    Stop a Dokku app.
    """
    command = f"ps:stop {app_name}"
    return await _execute(command)


async def destroy_app(app_name: str):
    """
    Permanently delete a Dokku app.
    """
    command = f"apps:destroy {app_name} --force"
    return await _execute(command)


async def sync_app_from_git_url(app_name: str, git_url: str):
    """
    Sync a Dokku app from a git repository. Url must include authentication.

    NOTE: This command can take a long time to complete. Best run as a background task.
    """
    command = f"git:sync --build-if-changes {app_name} {git_url}"
    return await _execute(command, timeout=600.0)  # 10 minute timeout for syncs


async def app_domains_report(app_name: str):
    """
    Get a report on the domains for a given app.
    """
    command = f"domains:report {app_name}"
    parser_func = dokku_parser.parse_report
    return await _execute(command, parser_func)


async def set_app_build_dir(app_name: str, build_dir: str):
    """
    Set the build directory for a Dokku app.
    """
    command = f"builder:set {app_name} build-dir {build_dir}"
    return await _execute(command)


async def set_app_git_branch(app_name: str, branch_name: str):
    """
    Set the git branch to deploy for a Dokku app.
    """
    command = f"git:set {app_name} deploy-branch {branch_name}"
    return await _execute(command)


async def enable_lets_encrypt(app_name: str):
    """
    Enable Let's Encrypt for a Dokku app.
    """
    command = f"letsencrypt:enable {app_name}"
    return await _execute(command)


# ======================================================= Plugins
async def list_plugins():
    """
    List all Dokku plugins.
    """
    command = "plugin:list"
    return await _execute(command)


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

    return await _execute(command)


# ======================================================= Databases
async def create_database(plugin_name: str, database_name: str):
    """
    Create a new Dokku database.
    """
    _ensure_database_supported(plugin_name)
    command = f"{plugin_name}:create {database_name}"
    return await _execute(command)


async def link_database(plugin_name: str, database_name: str, app_name: str):
    """
    Link a database to an app.
    """
    _ensure_database_supported(plugin_name)
    command = f"{plugin_name}:link {database_name} {app_name}"
    return await _execute(command)


# ======================================================= Execution
async def _execute(command: str, parser_func: callable = None, timeout: float = 60.0):
    """
    Execute a Dokku command and optionally parse its data.

    Args:
        command (str): The Dokku command to execute.
        parser_func (callable, optional): The function to parse the command data.
        timeout (float, optional): Maximum time to wait for response in seconds. Defaults to 60.0.

    Returns:
        The parsed output of the command or the raw output if no parser is provided.

    Raises:
        DokkuCommandError: If the command execution fails.
        DokkuParseError: If the output parsing fails.
    """
    response = await dokku_client.execute(command, timeout=timeout)
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
