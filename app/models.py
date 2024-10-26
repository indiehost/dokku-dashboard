from typing import Any, Optional

from pydantic import BaseModel


# ======================================================= Dokku
class DokkuCommandRequest(BaseModel):
    command: str


class DokkuResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class DokkuAppCreate(BaseModel):
    name: str


class DokkuPluginInstall(BaseModel):
    name: str


class DokkuDatabaseCreate(BaseModel):
    plugin_name: str
    database_name: str


class DokkuDatabaseLink(BaseModel):
    plugin_name: str
    database_name: str
    app_name: str
