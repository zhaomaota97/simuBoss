from typing import Any

from pydantic import BaseModel, Field


class WorkspaceDocumentIn(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


class WorkspaceDocumentOut(BaseModel):
    kind: str
    data: dict[str, Any] = Field(default_factory=dict)


class WorkspaceBundleOut(BaseModel):
    documents: dict[str, dict[str, Any]] = Field(default_factory=dict)
