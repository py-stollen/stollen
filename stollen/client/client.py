from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Iterable, Optional, Self, TypeVar

from ..exceptions import StollenAPIError
from ..session.aiohttp import AiohttpSession

if TYPE_CHECKING:
    from ..method import StollenMethod
    from ..session.base import BaseSession
    from ..types import StollenT
    from .api_access import APIAccessNode, BaseAPIAccessNodeFactory


class Stollen:
    session: BaseSession
    base_url: str
    api_access_nodes: Optional[Iterable[APIAccessNode | BaseAPIAccessNodeFactory]]
    use_method_placeholders: bool
    response_data_key: Optional[Iterable[str]]
    error_message_key: Optional[Iterable[str]]
    general_error_class: type[StollenAPIError]
    error_codes: dict[int, type[StollenAPIError]]

    def __init__(
        self,
        *,
        session: Optional[BaseSession] = None,
        base_url: str,
        api_access_nodes: Optional[Iterable[APIAccessNode | BaseAPIAccessNodeFactory]] = None,
        use_method_placeholders: bool = False,
        response_data_key: Optional[Iterable[str]] = None,
        error_message_key: Optional[Iterable[str]] = None,
        general_error_class: type[StollenAPIError] = StollenAPIError,
        error_codes: Optional[dict[int, type[StollenAPIError]]] = None,
    ) -> None:
        if session is None:
            session = AiohttpSession()
        self.session = session
        self.base_url = base_url
        self.api_access_nodes = api_access_nodes
        self.use_method_placeholders = use_method_placeholders
        self.response_data_key = response_data_key
        self.error_message_key = error_message_key
        self.general_error_class = general_error_class
        self.error_codes = error_codes or {}

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
