from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class StollenRequest(BaseModel):
    url: str
    method: str
    headers: dict[str, Any] = Field(default_factory=dict)
    query: dict[str, str] = Field(default_factory=dict)
    body: Optional[Any] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StollenResponse(BaseModel):
    status_code: int
    headers: dict[str, Any] = Field(default_factory=dict)
    body: Optional[Any] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
