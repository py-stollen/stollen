from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .input_file import InputFile


class StollenRequest(BaseModel):
    url: str
    http_method: str
    response_data_key: list[str]
    headers: dict[str, Any] = Field(default_factory=dict)
    query: dict[str, Union[str, int, float]] = Field(default_factory=dict)
    body: Optional[Any] = None
    files: Optional[dict[str, InputFile]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StollenResponse(BaseModel):
    status_code: int
    headers: dict[str, Any] = Field(default_factory=dict)
    body: Optional[Any] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
