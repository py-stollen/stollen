from __future__ import annotations

import json
from ssl import SSLContext, create_default_context
from typing import TYPE_CHECKING, Any, AsyncGenerator, Optional, cast

import certifi
from aiohttp import ClientResponse, ClientSession, FormData, TCPConnector, hdrs

from ..const import DEFAULT_CHUNK_SIZE, DEFAULT_REQUEST_TIMEOUT
from ..requests.input_file import InputFile
from ..requests.types import StollenRequest, StollenResponse
from .base import BaseSession

if TYPE_CHECKING:
    from ..client import StollenClientT
    from ..types import JsonDumps, JsonLoads


class AiohttpSession(BaseSession):
    _session: Optional[ClientSession]
    _ssl_context: SSLContext
    _should_reset_connector: bool

    def __init__(
        self,
        *,
        json_loads: JsonLoads = json.loads,
        json_dumps: JsonDumps = json.dumps,
        exclude_none_in_methods: bool = True,
    ) -> None:
        super().__init__(
            json_loads=json_loads,
            json_dumps=json_dumps,
            exclude_none_in_methods=exclude_none_in_methods,
        )
        self._session = None
        self._ssl_context = create_default_context(cafile=certifi.where())
        self._should_reset_connector = True

    async def get_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=TCPConnector(limit=100, ssl=self._ssl_context),
                json_serialize=self.json_dumps,
            )
            self._should_reset_connector = False

        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    def build_form_data(self, client: StollenClientT, request: StollenRequest) -> FormData:
        form: FormData = FormData(quote_fields=False)
        body: dict[str, Any] = cast(dict[str, Any], request.body)
        files: dict[str, InputFile] = cast(dict[str, InputFile], request.files)

        for name, value in body.items():
            form.add_field(name, self.json_dumps(value))

        for name, file in files.items():
            form.add_field(
                name,
                file.read(client),
                filename=file.filename or name,
            )

        return form

    async def make_request(
        self,
        client: StollenClientT,
        request: StollenRequest,
        request_timeout: int,
    ) -> tuple[StollenResponse, Any]:
        body_kwargs: dict[str, Any] = {}
        if isinstance(request.body, (str, bytes)):
            body_kwargs["data"] = request.body
        elif request.files:
            body_kwargs["data"] = self.build_form_data(client=client, request=request)
        else:
            body_kwargs["json"] = request.body

        session: ClientSession = await self.get_session()
        response: ClientResponse = await session.request(
            method=request.http_method,
            url=request.url,
            headers=request.headers,
            params=request.query,
            verify_ssl=False,
            timeout=request_timeout,
            **body_kwargs,
        )

        body: Any = await response.text()
        if response.headers.get(hdrs.CONTENT_TYPE, "").startswith("application/json"):
            body = self.json_loads(body)

        raw_response: StollenResponse = StollenResponse(
            status_code=response.status,
            headers=dict(response.headers),
            body=body,
        )

        return raw_response, self.prepare_response(
            client=client,
            request=request,
            response=raw_response,
        )

    async def stream_content(
        self,
        url: str,
        headers: Optional[dict[str, Any]] = None,
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        if headers is None:
            headers = {}

        session: ClientSession = await self.get_session()
        async with session.get(
            url=url,
            timeout=timeout,
            headers=headers,
            raise_for_status=raise_for_status,
        ) as resp:
            async for chunk in resp.content.iter_chunked(chunk_size):
                yield chunk
