from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Iterable, Optional, Self, TypeVar

from ..exceptions import DetailedStollenAPIError, StollenAPIError, StollenError
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
    global_request_fields: Iterable[RequestField | RequestFieldFactory]
    response_data_key: Optional[Iterable[str]]
    error_message_key: Optional[Iterable[str]]
    general_error_class: type[StollenError]
    error_codes: dict[int, type[StollenError]]
    stringify_detailed_errors: bool

    def __init__(
        self,
        *,
        session: Optional[BaseSession] = None,
        base_url: str,
        default_subdomain: Optional[str] = None,
        global_request_fields: Optional[Iterable[RequestField | RequestFieldFactory]] = None,
        response_data_key: Optional[Iterable[str]] = None,
        error_message_key: Optional[Iterable[str]] = None,
        general_error_class: type[StollenError] = StollenAPIError,
        error_codes: Optional[dict[int, type[StollenError]]] = None,
        raise_detailed_errors: bool = False,
        stringify_detailed_errors: bool = True,
    ) -> None:
        if session is None:
            session = AiohttpSession()
        if raise_detailed_errors and general_error_class is StollenAPIError:
            general_error_class = DetailedStollenAPIError
        self.session = session
        self.base_url = base_url
        self.default_subdomain = default_subdomain
        self.global_request_fields = global_request_fields or []
        self.response_data_key = response_data_key
        self.error_message_key = error_message_key
        self.general_error_class = general_error_class
        self.error_codes = error_codes or {}
        self.stringify_detailed_errors = stringify_detailed_errors

    async def __call__(self, method: StollenMethod[StollenT, StollenClientT]) -> StollenT:
        return await self.session(client=self, method=method)

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
