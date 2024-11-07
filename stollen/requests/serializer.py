from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Iterable, Optional, cast

from pydantic import RootModel

from ..enums import RequestFieldType
from ..requests.fields import RequestField
from ..requests.input_file import InputFile
from ..requests.types import StollenRequest

if TYPE_CHECKING:
    from ..client import Stollen, StollenClientT
    from ..method import StollenMethod
    from ..requests.factory import RequestFieldFactory
    from ..types import JsonDumps, JsonLoads, StollenT


class RequestSerializer:
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
        payload: dict[str, Any] = self.prepare_payload(client=client, method=method)

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
