from __future__ import annotations

import io
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, Optional, Union

import aiofiles

from ..const import DEFAULT_CHUNK_SIZE, DEFAULT_REQUEST_TIMEOUT

if TYPE_CHECKING:
    from ..client import Stollen


class InputFile(ABC):
    def __init__(
        self,
        filename: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        self.filename = filename
        self.chunk_size = chunk_size

    @abstractmethod
    async def read(self, client: Stollen) -> AsyncGenerator[bytes, None]:
        yield b""


class BufferedInputFile(InputFile):
    def __init__(self, file: bytes, filename: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """
        Represents object for uploading files from filesystem

        :param file: Bytes
        :param filename: Filename to be propagated to telegram.
        :param chunk_size: Uploading chunk size
        """
        super().__init__(filename=filename, chunk_size=chunk_size)

        self.data = file

    @classmethod
    def from_file(
        cls,
        path: Union[str, Path],
        filename: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> BufferedInputFile:
        """
        Create buffer from file

        :param path: Path to file
        :param filename: Filename to be propagated to telegram.
            By default, will be parsed from path
        :param chunk_size: Uploading chunk size
        :return: instance of :obj:`BufferedInputFile`
        """
        if filename is None:
            filename = os.path.basename(path)
        with open(path, "rb") as f:
            data = f.read()
        return cls(data, filename=filename, chunk_size=chunk_size)

    async def read(self, client: Stollen) -> AsyncGenerator[bytes, None]:
        buffer = io.BytesIO(self.data)
        while chunk := buffer.read(self.chunk_size):
            yield chunk


class FSInputFile(InputFile):
    def __init__(
        self,
        path: Union[str, Path],
        filename: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> None:
        """
        Represents object for uploading files from filesystem

        :param path: Path to file
        :param filename: Filename to be propagated to telegram.
            By default, will be parsed from path
        :param chunk_size: Uploading chunk size
        """
        if filename is None:
            filename = os.path.basename(path)
        super().__init__(filename=filename, chunk_size=chunk_size)
        self.path = path

    async def read(self, client: Stollen) -> AsyncGenerator[bytes, None]:
        async with aiofiles.open(self.path, "rb") as f:
            while chunk := await f.read(self.chunk_size):
                yield chunk


class URLInputFile(InputFile):
    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        filename: Optional[str] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
        client: Optional[Stollen] = None,
    ) -> None:
        super().__init__(filename=filename, chunk_size=chunk_size)
        if headers is None:
            headers = {}
        self.url = url
        self.headers = headers
        self.timeout = timeout
        self.client = client

    async def read(self, client: Stollen) -> AsyncGenerator[bytes, None]:
        client = self.client or client
        async for chunk in client.session.stream_content(
            url=self.url,
            headers=self.headers,
            timeout=self.timeout,
            chunk_size=self.chunk_size,
            raise_for_status=True,
        ):
            yield chunk
