from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Iterable, Optional, cast

from pydantic import BaseModel, RootModel

# noinspection PyProtectedMember
from pydantic.fields import FieldInfo

from ..const import DEFAULT_CHUNK_SIZE
from ..enums import RequestFieldType
from ..requests.fields import RequestField
from ..requests.input_file import InputFile
from ..requests.types import StollenRequest
from .types import FileResponse

if TYPE_CHECKING:
    from ..client import Stollen, StollenClientT
    from ..method import StollenMethod
    from ..requests.factory import RequestFieldFactory
    from ..types import JsonDumps, JsonLoads, StollenT


class RequestSerializer:
    json_loads: JsonLoads
    json_dumps: JsonDumps
    exclude_defaults: bool

    def __init__(
        self,
        *,
        json_loads: JsonLoads = json.loads,
        json_dumps: JsonDumps = json.dumps,
        exclude_defaults: bool = True,
    ) -> None:
        self.json_loads = json_loads
        self.json_dumps = json_dumps
        self.exclude_defaults = exclude_defaults

    @classmethod
    def format_url(cls, url: str, payload: dict[str, dict[str, Any]]) -> str:
        to_format: dict[str, Any] = {}
        for data in payload.values():
            for key in data.copy():
                if f"{{{key}}}" in url:
                    to_format[key] = data.pop(key)
        return url.format(**to_format)

    def _prepare_field(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
        default_field_type: str,
        field: FieldInfo,
        field_value: Any,
    ) -> tuple[str, Any]:
        field_type = cast(
            str,
            (
                field.json_schema_extra.get("field_type", default_field_type)
                if isinstance(field.json_schema_extra, dict)
                else default_field_type
            ),
        )

        if field_value is None:
            field_factory: Optional[RequestFieldFactory] = (
                field.json_schema_extra.get("field_factory")  # type: ignore[assignment]
                if isinstance(field.json_schema_extra, dict)
                else None
            )

            if field_factory is not None:
                field_value = field_factory(client, method)  # type: ignore[arg-type]

            if isinstance(field_value, BaseModel):
                field_value = field_value.model_dump(exclude_defaults=self.exclude_defaults)

            if field_value is None:
                return field_type, None

        if field_type == RequestFieldType.QUERY and not isinstance(
            field_value,
            (str, int, float),
        ):
            field_value = self.json_dumps(field_value)

        return field_type, field_value

    def _prepare_method_fields(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
        default_field_type: str,
        payload: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        dump: dict[str, Any] = method.model_dump(
            by_alias=True,
            exclude_defaults=self.exclude_defaults,
        )

        for name, field in method.model_fields.items():
            key: str = field.serialization_alias or field.alias or name

            field_value = dump.get(key)
            if isinstance(field_value, InputFile):
                payload[RequestFieldType.FILE][key] = field_value
                continue

            field_type, field_value = self._prepare_field(
                client=client,
                method=method,
                default_field_type=default_field_type,
                field=field,
                field_value=field_value,
            )
            if field_value is None and self.exclude_defaults:
                continue

            fields = payload.setdefault(field_type, {})
            fields[key] = field_value

        return payload

    def prepare_payload(
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
            RequestFieldType.PLACEHOLDER: {},
            RequestFieldType.BODY: {},
            RequestFieldType.QUERY: {},
            RequestFieldType.HEADER: {},
            RequestFieldType.FILE: {},
        }

        for g_field in client.global_request_fields:
            if callable(g_field):
                g_field = g_field(client, method)  # type: ignore[assignment, arg-type]
            if isinstance(g_field, Iterable):
                for _g_field in g_field:
                    payload[_g_field.type][_g_field.name] = _g_field.dump()
                continue
            if g_field is None:
                continue
            g_field = cast(RequestField, g_field)
            payload[g_field.type][g_field.name] = g_field.dump()

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
        payload: dict[str, Any] = self.prepare_payload(client=client, method=method)

        raw_url: str = client.base_url
        if "{subdomain}" in raw_url:
            subdomain: Optional[str] = client.stollen_get_subdomain(method=method)
            if subdomain is None:
                raise ValueError("Request subdomain is missing!")
            raw_url = raw_url.format(subdomain=subdomain)

        url: str = self.format_url(
            url=f"{raw_url}/{method.api_method.removeprefix('/')}",
            payload=payload,
        )

        try:
            stream_content: bool = issubclass(method.returning, FileResponse)
            stream_chunk_size: Optional[int] = (
                getattr(method, "chunk_size", DEFAULT_CHUNK_SIZE) if stream_content else None
            )
        except TypeError:
            stream_content = False
            stream_chunk_size = None

        return StollenRequest(
            url=url,
            http_method=method.http_method,
            response_data_key=method.response_data_key,
            headers=payload.pop(RequestFieldType.HEADER, {}),
            query=payload.pop(RequestFieldType.QUERY, {}),
            body=payload.pop(RequestFieldType.BODY, {}),
            files=payload.pop(RequestFieldType.FILE, {}),
            stream_content=stream_content,
            stream_chunk_size=stream_chunk_size,
        )
