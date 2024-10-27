from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


# ======================================================= Database
class GitHubAppCredentials(SQLModel, table=True):
    __tablename__ = "github_app_credentials"

    id: Optional[int] = Field(default=None, primary_key=True)
    app_id: str
    app_name: str
    client_id: str
    client_secret_encrypted: str
    private_key_encrypted: str
    webhook_secret_encrypted: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


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
