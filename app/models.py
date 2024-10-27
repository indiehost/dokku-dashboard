from typing import Any, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# ======================================================= Database
class Test(SQLModel, table=True):
    """
    Temp test model for database testing in dokku
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None


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
