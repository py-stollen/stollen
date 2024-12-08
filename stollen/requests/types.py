import asyncio
from io import BytesIO
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .input_file import InputFile


class StollenRequest(BaseModel):
    url: str
    http_method: str
    response_data_key: list[str] = Field(default_factory=list)
    headers: dict[str, Any] = Field(default_factory=dict)
    query: dict[str, Union[str, int, float]] = Field(default_factory=dict)
    body: Optional[Any] = None
    files: Optional[dict[str, InputFile]] = None
    stream_content: bool = False
    stream_chunk_size: Optional[int] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StollenResponse(BaseModel):
    status_code: int
    headers: dict[str, Any] = Field(default_factory=dict)
    body: Optional[Any] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FileResponse(BaseModel):
    file: BytesIO
    size: Optional[int] = None
    content_type: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def _in_memory(self) -> bool:
        rolled_to_disk: bool = getattr(self.file, "_rolled", True)
        return not rolled_to_disk

    async def write(self, data: bytes) -> None:
        if self.size is not None:
            self.size += len(data)

        if self._in_memory:
            self.file.write(data)
        else:
            await asyncio.to_thread(self.file.write, data)

    async def read(self, size: int = -1) -> bytes:
        if self._in_memory:
            return self.file.read(size)
        return await asyncio.to_thread(self.file.read, size)

    async def seek(self, offset: int, whence: int = 0) -> None:
        if self._in_memory:
            self.file.seek(offset, whence)
        else:
            await asyncio.to_thread(self.file.seek, offset, whence)

    async def close(self) -> None:
        if self._in_memory:
            self.file.close()
        else:
            await asyncio.to_thread(self.file.close)
