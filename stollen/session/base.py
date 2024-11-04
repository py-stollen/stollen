from __future__ import annotations

import json
from abc import ABC, abstractmethod
from types import TracebackType
from typing import TYPE_CHECKING, Any, AsyncGenerator, Iterable, Optional, cast

from pydantic import RootModel, TypeAdapter, ValidationError
from typing_extensions import Self

from .. import loggers
from ..const import DEFAULT_CHUNK_SIZE, DEFAULT_REQUEST_TIMEOUT
from ..enums import RequestFieldType
from ..exceptions import DetailedStollenAPIError, StollenError
from ..requests.fields import RequestField
from ..requests.input_file import InputFile
from ..requests.types import StollenRequest, StollenResponse
from ..utils.mapping import recursive_getitem

if TYPE_CHECKING:
    from ..client import Stollen, StollenClientT
    from ..method import StollenMethod
    from ..requests.factory import RequestFieldFactory
    from ..types import JsonDumps, JsonLoads, StollenT


class BaseSession(ABC):
    """
    This is base class for HTTP sessions of your stollen client
    If you want to create your own session, you must inherit from this class.
    """

    json_loads: JsonLoads
    json_dumps: JsonDumps
    exclude_none_in_methods: bool

    def __init__(
        self,
        *,
        json_loads: JsonLoads = json.loads,
        json_dumps: JsonDumps = json.dumps,
        exclude_none_in_methods: bool = True,
    ) -> None:
        self.json_loads = json_loads
        self.json_dumps = json_dumps
        self.exclude_none_in_methods = exclude_none_in_methods

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
        request_timeout: int,
    ) -> tuple[StollenResponse, Any]:
        pass

    @abstractmethod
    async def stream_content(
        self,
        url: str,
        headers: Optional[dict[str, Any]] = None,
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        raise_for_status: bool = True,
    ) -> AsyncGenerator[bytes, None]:
        yield b""

    @classmethod
    def prepare_response(
        cls,
        client: Stollen,
        request: StollenRequest,
        response: StollenResponse,
    ) -> Any:
        try:
            if response.status_code not in client.error_codes and response.status_code < 400:
                response_data_key: list[str] = client.response_data_key.copy()
                response_data_key.extend(request.response_data_key)
                return recursive_getitem(
                    mapping=response.body,
                    keys=response_data_key,
                )
            exception_type: type[StollenError] = (
                client.error_codes.get(
                    response.status_code,
                    client.general_error_class,
                )
                if not client.force_detailed_errors
                else DetailedStollenAPIError
            )
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

    @classmethod
    def format_method(
        cls,
        method: StollenMethod[StollenT, StollenClientT],
        payload: dict[str, Any],
    ) -> str:
        return method.api_method.format(
            **{
                key: payload.pop(key)
                for key in payload.copy()
                if f"{{{key}}}" in method.api_method
            }
        )

    def _prepare_method_fields(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
        default_field_type: str,
        payload: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        dump: dict[str, Any] = method.model_dump()
        for name, field in method.model_fields.items():
            field_value = dump.get(name)

            if isinstance(field_value, InputFile):
                payload[RequestFieldType.FILE][name] = field_value
                continue

            if field_value is None:
                field_factory: Optional[RequestFieldFactory] = (
                    field.json_schema_extra.get("field_factory")  # type: ignore[assignment]
                    if isinstance(field.json_schema_extra, dict)
                    else None
                )
                if field_factory is not None:
                    field_value = field_factory(client, method)  # type: ignore[arg-type]
                if field_value is None and self.exclude_none_in_methods:
                    continue
            field_type = cast(
                str,
                (
                    field.json_schema_extra.get("field_type", default_field_type)
                    if isinstance(field.json_schema_extra, dict)
                    else default_field_type
                ),
            )
            fields = payload.setdefault(field_type, {})
            if field_type == RequestFieldType.QUERY and not isinstance(
                field_value,
                (str, int, float),
            ):
                field_value = self.json_dumps(field_value)
            fields[field.serialization_alias or name] = field_value

        return payload

    def _prepare_payload(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
    ) -> dict[str, Any]:
        default_field_type: str = (
            method.default_field_type
            if method.default_field_type != RequestFieldType.AUTO
            else RequestFieldType.resolve(http_method=method.http_method)
        )

        # For non-dictionary models
        if isinstance(method, RootModel):
            return {default_field_type: method.model_dump()}

        payload: dict[str, dict[str, Any]] = {
            RequestFieldType.BODY: {},
            RequestFieldType.QUERY: {},
            RequestFieldType.HEADER: {},
            RequestFieldType.PLACEHOLDER: {},
            RequestFieldType.FILE: {},
        }

        for g_field in client.global_request_fields:
            if callable(g_field):
                g_field = g_field(client, method)  # type: ignore[assignment, arg-type]
            if isinstance(g_field, Iterable):
                for _g_field in g_field:
                    payload[_g_field.type][_g_field.name] = _g_field.value
                continue
            g_field = cast(RequestField, g_field)
            payload[g_field.type][g_field.name] = g_field.value

        return self._prepare_method_fields(
            client=client,
            method=method,
            default_field_type=default_field_type,
            payload=payload,
        )

    def to_request(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
    ) -> StollenRequest:
        payload: dict[str, Any] = self._prepare_payload(client=client, method=method)

        raw_url: str = client.base_url
        if "{subdomain}" in raw_url:
            subdomain: Optional[str] = client.stollen_get_subdomain(method=method)
            if subdomain is None:
                raise ValueError("Request subdomain is missing!")
            raw_url = raw_url.format(subdomain=subdomain)

        to_format: dict[str, Any] = {}
        for data in payload.values():
            if not isinstance(data, dict):
                continue
            to_format.update(data)

        api_method: str = self.format_method(
            method=method,
            payload=to_format,
        )
        raw_url = f"{raw_url}/{api_method.removeprefix('/')}"

        return StollenRequest(
            url=raw_url.format(**payload.pop(RequestFieldType.PLACEHOLDER, {})),
            http_method=method.http_method,
            response_data_key=method.response_data_key,
            headers=payload.pop(RequestFieldType.HEADER, {}),
            query=payload.pop(RequestFieldType.QUERY, {}),
            body=payload.pop(RequestFieldType.BODY, {}),
            files=payload.pop(RequestFieldType.FILE, {}),
        )

    async def __call__(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
        request_timeout: int = DEFAULT_REQUEST_TIMEOUT,
    ) -> StollenT:
        request: StollenRequest = self.to_request(client=client, method=method)
        loggers.client.debug(
            "Making %s request to the endpoint %s",
            request.http_method,
            request.url,
        )
        response, data = await self.make_request(
            client=client,
            request=request,
            request_timeout=request_timeout,
        )
        loggers.client.debug(
            "%s request to the endpoint %s has been made with status code %d",
            request.http_method,
            request.url,
            response.status_code,
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
