from __future__ import annotations

import asyncio
from io import BytesIO
from ssl import create_default_context
from typing import TYPE_CHECKING, Any, Optional, cast

import certifi
from aiohttp import ClientResponse, ClientSession, FormData, TCPConnector

from ...const import DEFAULT_REQUEST_TIMEOUT
from ...requests import FileResponse, InputFile, RequestSerializer, StollenRequest, StollenResponse
from ..base import BaseSession
from .proxy import ProxyType, prepare_connector

if TYPE_CHECKING:
    from ...client import StollenClientT


class AiohttpSession(BaseSession):
    _session: Optional[ClientSession]
    _connector_type: type[TCPConnector]
    _connector_kwargs: dict[str, Any]
    _should_reset_connector: bool
    _proxy: Optional[ProxyType]

    def __init__(
        self,
        serializer: RequestSerializer = RequestSerializer(),
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
        limit: int = 100,
        proxy: Optional[ProxyType] = None,
        **connector_kwargs: Any,
    ) -> None:
        """
        Client session based on aiohttp.

        :param limit: The total number of simultaneous connections. Default is 100.
        :param proxy: The proxy to be used for requests. Default is None.
        :param connector_kwargs: Additional connector kwargs.
        """
        super().__init__(serializer=serializer, timeout=timeout)
        self._session = None
        self._connector_type = TCPConnector
        self._connector_kwargs = {
            "ssl": create_default_context(cafile=certifi.where()),
            "limit": limit,
        }
        self._connector_kwargs.update(connector_kwargs)
        self._should_reset_connector = True
        self._proxy = proxy
        if proxy is not None:
            try:
                self.setup_proxy(proxy)
            except ImportError as error:
                raise RuntimeError(
                    "In order to use aiohttp client for proxy requests, install "
                    "https://pypi.org/project/aiohttp-socks/."
                    "You can do it by running `pip install stollen[proxy]`."
                ) from error

    @property
    def proxy(self) -> Optional[ProxyType]:
        return self._proxy

    def setup_proxy(self, proxy: ProxyType) -> None:
        self._connector_type, self._connector_kwargs = prepare_connector(proxy)
        self._proxy = proxy
        self._should_reset_connector = True

    async def get_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_kwargs),
                json_serialize=self.serializer.json_dumps,
            )
            self._should_reset_connector = False

        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

            # Wait 250 ms for the underlying SSL connections to close
            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)

    def build_form_data(self, client: StollenClientT, request: StollenRequest) -> FormData:
        form: FormData = FormData(quote_fields=False)
        body: dict[str, Any] = cast(dict[str, Any], request.body)
        files: dict[str, InputFile] = cast(dict[str, InputFile], request.files)

        for name, value in body.items():
            if not isinstance(value, (str, int, float)):
                value = self.json_dumps(value)
            form.add_field(name, str(value))

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
        request_timeout: Optional[int] = None,
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
            timeout=request_timeout or self.timeout,
            **body_kwargs,
        )

        if not request.stream_content:
            if response.content_type.startswith("application/json"):
                body = await response.json(loads=self.serializer.json_loads)
            else:
                body = await response.text()
        else:
            buffer: BytesIO = BytesIO()
            async for chunk in response.content.iter_chunked(cast(int, request.stream_chunk_size)):
                # noinspection PyTypeChecker
                buffer.write(chunk)
            buffer.seek(0)
            body = FileResponse(
                file=buffer,
                size=response.content_length,
                content_type=response.content_type,
            )

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
