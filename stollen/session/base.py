from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from types import TracebackType
from typing import TYPE_CHECKING, Any, Optional

from pydantic import TypeAdapter, ValidationError
from typing_extensions import Self

from .. import loggers
from ..const import DEFAULT_REQUEST_TIMEOUT
from ..exceptions import DetailedStollenAPIError, StollenAPIError, StollenError
from ..requests.serializer import RequestSerializer
from ..requests.types import StollenRequest, StollenResponse
from ..utils.mapping import recursive_getitem

if TYPE_CHECKING:
    from ..client import Stollen, StollenClientT
    from ..method import StollenMethod
    from ..types import JsonDumps, JsonLoads, StollenT


def pre_log_request(request: StollenRequest) -> None:
    loggers.client.info(
        "Pending HTTP Request: %s %s",
        request.http_method,
        request.url,
    )


def log_request(
    request: StollenRequest,
    response: StollenResponse,
    loop: AbstractEventLoop,
    start_time: float,
) -> None:
    args: tuple[Any, ...] = (
        "HTTP Request: %s %s (ok=%s, status_code=%d, duration=%dms)",
        request.http_method,
        request.url,
        response.status_code < 400,
        response.status_code,
        (loop.time() - start_time) * 1000,
    )

    if response.status_code < 400:
        loggers.client.info(*args)
    else:
        loggers.client.error(*args)


class BaseSession(ABC):
    """
    This is base class for HTTP sessions of your stollen client
    If you want to create your own session, you must inherit from this class.
    """

    json_loads: JsonLoads
    json_dumps: JsonDumps
    exclude_defaults: bool
    serializer: RequestSerializer
    timeout: int

    def __init__(
        self,
        *,
        serializer: RequestSerializer = RequestSerializer(),
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        self.json_loads = serializer.json_loads
        self.json_dumps = serializer.json_dumps
        self.exclude_defaults = serializer.exclude_defaults
        self.serializer = serializer
        self.timeout = timeout

    @abstractmethod
    async def close(self) -> None:
        """
        Close client session
        """
        pass

    @abstractmethod
    async def make_request(
        self,
        client: StollenClientT,
        request: StollenRequest,
        request_timeout: Optional[int] = None,
    ) -> tuple[StollenResponse, Any]:
        pass

    @classmethod
    def get_exc_type(cls, client: StollenClientT, response: StollenResponse) -> type[StollenError]:
        return (
            client.error_codes.get(
                response.status_code,
                client.general_error_class,
            )
            if not client.force_detailed_errors
            else DetailedStollenAPIError
        )

    @classmethod
    def prepare_response(
        cls,
        client: Stollen,
        request: StollenRequest,
        response: StollenResponse,
    ) -> Any:
        for header in client.hide_headers:
            if header not in response.headers:
                continue
            response.headers[header] = "********"

        try:
            if response.status_code not in client.error_codes and response.status_code < 400:
                response_data_key: list[str] = client.response_data_key.copy()
                response_data_key.extend(request.response_data_key)
                return recursive_getitem(mapping=response.body, keys=response_data_key)

            exception_type: type[StollenError] = cls.get_exc_type(client, response)
            raise exception_type(
                message=str(
                    recursive_getitem(
                        mapping=response.body,
                        keys=client.error_message_key,
                    )
                ),
                request=request,
                response=response,
                stringify=client.stringify_detailed_errors,
            )

        except KeyError:
            raise DetailedStollenAPIError(
                message="An error has occurred and stollen can't parse the response.",
                request=request,
                response=response,
                stringify=client.stringify_detailed_errors,
            )

    async def raw_request(
        self,
        client: Stollen,
        request: StollenRequest,
        request_timeout: Optional[int] = None,
    ) -> tuple[StollenResponse, Any]:
        loop: AbstractEventLoop = asyncio.get_running_loop()
        start_time: float = loop.time()

        try:
            if client.echo_requests:
                pre_log_request(request=request)
            response, data = await self.make_request(
                client=client,
                request=request,
                request_timeout=request_timeout,
            )
        except StollenAPIError as error:
            if client.echo_requests:
                log_request(
                    request=request,
                    response=error.response,
                    loop=loop,
                    start_time=start_time,
                )
            raise

        if client.echo_requests:
            log_request(request=request, response=response, loop=loop, start_time=start_time)

        return response, data

    async def __call__(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
        request_timeout: Optional[int] = None,
    ) -> StollenT:
        request: StollenRequest = self.serializer.to_request(client=client, method=method)
        response, data = await self.raw_request(
            client=client,
            request=request,
            request_timeout=request_timeout,
        )

        adapter: TypeAdapter[StollenT] = method.type_adapter
        try:
            return adapter.validate_python(data, context={"client": client})
        except ValidationError as error:
            raise DetailedStollenAPIError(
                message="An error has occurred while validating the response.",
                request=request,
                response=response,
                stringify=client.stringify_detailed_errors,
            ) from error

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()
