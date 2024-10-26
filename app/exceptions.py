from fastapi import Request, status
from fastapi.responses import JSONResponse


# ======================================================= Exceptions
class DokkuCommandError(Exception):
    """
    Base exception for Dokku command errors
    """

    pass


class DokkuParseError(Exception):
    """
    Exception for Dokku output parsing errors
    """

    pass


class DokkuInvalidCommandError(Exception):
    """
    Exception for invalid Dokku commands
    """

    pass


# ======================================================= Handlers
def generic_exception_handler(request: Request, err: Exception):
    """
    Generic exception handler - returns a 500 status code.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "message": str(err)},
    )


def dokku_command_exception_handler(request: Request, ex: DokkuCommandError):
    """
    DokkuCommandError - handles Dokku command errors
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Dokku Command Error",
            "message": str(ex),
        },
    )


def dokku_parse_exception_handler(request: Request, ex: DokkuParseError):
    """
    DokkuParseError - handles Dokku output parsing errors
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Dokku Parse Error",
            "message": str(ex),
        },
    )


def dokku_invalid_command_exception_handler(request: Request, ex: DokkuInvalidCommandError):
    """
    DokkuInvalidCommand - handles invalid Dokku commands
    """
    return JSONResponse(status_code=400, content={"error": "Invalid Command", "message": str(ex)})
