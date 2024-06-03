from __future__ import annotations

import json
from ssl import SSLContext, create_default_context
from typing import TYPE_CHECKING, Any, Optional

import certifi
from aiohttp import ClientResponse, ClientSession, TCPConnector

from ..enums import HTTPMethod
from .base import BaseSession

if TYPE_CHECKING:
    from ..client import StollenClientT
    from ..types import HTTPMethodType, JsonDumps, JsonLoads


class AiohttpSession(BaseSession):
    _session: Optional[ClientSession]
    _ssl_context: SSLContext
    _should_reset_connector: bool

    def __init__(
        self,
        *,
        json_loads: JsonLoads = json.loads,
        json_dumps: JsonDumps = json.dumps,
        use_dump_aliases: bool = True,
        exclude_none_in_methods: bool = True,
    ) -> None:
        super().__init__(
            json_loads=json_loads,
            json_dumps=json_dumps,
            use_dump_aliases=use_dump_aliases,
            exclude_none_in_methods=exclude_none_in_methods,
        )

        self._session = None
        self._ssl_context = create_default_context(cafile=certifi.where())
        self._should_reset_connector = True

    def resolve_request_kwargs(
        self, method: HTTPMethodType, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if method in [HTTPMethod.GET, HTTPMethod.HEAD, HTTPMethod.OPTIONS, HTTPMethod.TRACE]:
            return {
                "params": {
                    k: self.json_dumps(v) if not isinstance(v, str) else v
                    for k, v in payload.items()
                }
            }
        if method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH, HTTPMethod.DELETE]:
            return {"json": payload}
        raise TypeError(f"Got an unexpected method type: {method}")

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
        method: HTTPMethodType,
        url: str,
        headers: dict[str, Any],
        payload: dict[str, Any],
    ) -> Any:
        session: ClientSession = await self.get_session()
        response: ClientResponse = await session.request(
            method=method,
            url=url,
            headers=headers,
            verify_ssl=False,
            **self.resolve_request_kwargs(method=method, payload=payload),
        )
        return self.prepare_response(
            client=client,
            response_data=await response.json(loads=self.json_loads),
            status=response.status,
        )
