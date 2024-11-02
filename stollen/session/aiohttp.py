from __future__ import annotations

import json
from ssl import SSLContext, create_default_context
from typing import TYPE_CHECKING, Any, Optional

import certifi
from aiohttp import ClientResponse, ClientSession, TCPConnector, hdrs

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

    async def make_request(
        self,
        client: StollenClientT,
        request: StollenRequest,
        request_timeout: int,
    ) -> tuple[StollenResponse, Any]:
        session: ClientSession = await self.get_session()
        body_kwargs: dict[str, Any] = (
            (
                {"data": request.body}
                if isinstance(request.body, (str, bytes))
                else {"json": request.body}
            )
            if request.body
            else {}
        )
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
