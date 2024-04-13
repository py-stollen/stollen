from __future__ import annotations

import json
from abc import ABC, abstractmethod
from types import TracebackType
from typing import TYPE_CHECKING, Any, Iterable, Optional, Self

from pydantic import TypeAdapter

from ..client.api_access import APIAccessNode, BaseAPIAccessNodeFactory
from ..enums import AccessNodeType
from ..exceptions import StollenAPIError
from ..utils.mapping import recursive_getitem

if TYPE_CHECKING:
    from ..client import Stollen, StollenClientT
    from ..method import StollenMethod
    from ..types import HTTPMethodType, JsonDumps, JsonLoads, StollenT


class BaseSession(ABC):
    """
    This is base class for HTTP sessions of your stollen client

    If you want to create your own session, you must inherit from this class.
    """

    json_loads: JsonLoads
    json_dumps: JsonDumps
    use_dump_aliases: bool
    exclude_none_in_methods: bool

    def __init__(
        self,
        *,
        json_loads: JsonLoads = json.loads,
        json_dumps: JsonDumps = json.dumps,
        use_dump_aliases: bool = True,
        exclude_none_in_methods: bool = True,
    ) -> None:
        self.json_loads = json_loads
        self.json_dumps = json_dumps
        self.use_dump_aliases = use_dump_aliases
        self.exclude_none_in_methods = exclude_none_in_methods

    @abstractmethod
    async def make_request(
        self,
        client: Stollen,
        method: HTTPMethodType,
        url: str,
        headers: dict[str, Any],
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close client session
        """
        pass

    @classmethod
    def prepare_response(cls, client: Stollen, response_data: Any, status: int) -> Any:
        if status in client.error_codes or status > 400:
            exception_type: type[StollenAPIError] = client.error_codes.get(
                status, client.general_error_class
            )
            raise exception_type(
                message=str(
                    recursive_getitem(mapping=response_data, keys=client.error_message_key)
                ),
                code=status,
                raw_response=response_data,
            )
        return recursive_getitem(mapping=response_data, keys=client.response_data_key)

    @classmethod
    def format_method(
        cls,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
        payload: dict[str, Any],
    ) -> str:
        if not client.use_method_placeholders:
            return method.api_method
        return method.api_method.format(
            **{
                key: payload.pop(key)
                for key in payload.copy()
                if f"{{{key}}}" in method.api_method
            }
        )

    def _apply_access_nodes(
        self,
        nodes: Iterable[BaseAPIAccessNodeFactory | APIAccessNode],
        headers: dict[str, Any],
        placeholders: dict[str, Any],
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
    ) -> None:
        for node in nodes:
            if isinstance(node, BaseAPIAccessNodeFactory):
                self._apply_access_nodes(
                    nodes=node.construct(client=client, method=method),  # type: ignore
                    headers=headers,
                    placeholders=placeholders,
                    client=client,
                    method=method,
                )
            elif node.type == AccessNodeType.HEADER:
                headers[node.name] = node.value
            elif node.type == AccessNodeType.URL_PLACEHOLDER:
                placeholders[node.name] = node.value

    def apply_access_nodes(
        self, url: str, client: Stollen, method: StollenMethod[StollenT, StollenClientT]
    ) -> tuple[str, dict[str, Any]]:
        if not client.api_access_nodes:
            return url, {}
        headers: dict[str, Any] = {}
        placeholders: dict[str, Any] = {}
        self._apply_access_nodes(
            nodes=client.api_access_nodes,
            headers=headers,
            placeholders=placeholders,
            client=client,
            method=method,
        )
        return url.format(**placeholders), headers

    async def __call__(
        self, client: Stollen, method: StollenMethod[StollenT, StollenClientT]
    ) -> StollenT:
        payload: dict[str, Any] = method.model_dump(
            by_alias=self.use_dump_aliases, exclude_none=self.exclude_none_in_methods
        )

        api_method: str = self.format_method(client=client, method=method, payload=payload)
        raw_url: str = f"{client.base_url}/{api_method.removeprefix('/')}"
        url, headers = self.apply_access_nodes(url=raw_url, client=client, method=method)
        raw_response: Any = await self.make_request(
            client=client, method=method.http_method, url=url, headers=headers, payload=payload
        )
        adapter: TypeAdapter[StollenT] = method.type_adapter
        return adapter.validate_python(raw_response, context={"client": client})

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await self.close()
