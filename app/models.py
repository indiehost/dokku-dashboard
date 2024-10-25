from typing import Any, Optional

from pydantic import BaseModel


# ======================================================= Dokku
class DokkuCommandRequest(BaseModel):
    command: str


class DokkuResponse(BaseModel):
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
