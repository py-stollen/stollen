from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Iterable, Optional, TypeVar, Union

from typing_extensions import Self

from ..exceptions import StollenAPIError, StollenError
from ..session.aiohttp import AiohttpSession

if TYPE_CHECKING:
    from ..method import StollenMethod
    from ..requests.factory import RequestFieldFactory
    from ..requests.fields import RequestField
    from ..session.base import BaseSession
    from ..types import StollenT


class Stollen:
    session: BaseSession
    base_url: str
    default_subdomain: Optional[str]
    global_request_fields: Iterable[Union[RequestField, RequestFieldFactory]]
    response_data_key: list[str]
    error_message_key: list[str]
    general_error_class: type[StollenError]
    error_codes: dict[int, type[StollenError]]
    force_detailed_errors: bool
    stringify_detailed_errors: bool

    def __init__(
        self,
        *,
        session: Optional[BaseSession] = None,
        base_url: str,
        default_subdomain: Optional[str] = None,
        global_request_fields: Optional[Iterable[Union[RequestField, RequestFieldFactory]]] = None,
        response_data_key: Optional[list[str]] = None,
        error_message_key: Optional[list[str]] = None,
        general_error_class: type[StollenError] = StollenAPIError,
        error_codes: Optional[dict[int, type[StollenError]]] = None,
        force_detailed_errors: bool = False,
        stringify_detailed_errors: bool = True,
    ) -> None:
        if session is None:
            session = AiohttpSession()
        self.session = session
        self.base_url = base_url
        self.default_subdomain = default_subdomain
        self.global_request_fields = global_request_fields or []
        self.response_data_key = response_data_key or []
        self.error_message_key = error_message_key or []
        self.general_error_class = general_error_class
        self.error_codes = error_codes or {}
        self.force_detailed_errors = force_detailed_errors
        self.stringify_detailed_errors = stringify_detailed_errors

    def stollen_get_subdomain(
        self,
        method: StollenMethod[StollenT, StollenClientT],
    ) -> Optional[str]:
        return method.subdomain or self.default_subdomain

    async def __call__(
        self,
        method: StollenMethod[StollenT, StollenClientT],
        request_timeout: Optional[int] = None,
    ) -> StollenT:
        return await self.session(
            client=self,
            method=method,
            request_timeout=request_timeout,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.session.close()


StollenClientT = TypeVar("StollenClientT", bound=Stollen)
