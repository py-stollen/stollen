from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

from ..enums import RequestFieldType

if TYPE_CHECKING:
    from .factory import AnyValueFactory


@dataclass()
class RequestField:
    name: str
    value: Any
    type: str

    def dump(self) -> Any:
        if isinstance(self.value, BaseModel):
            return self.value.model_dump()
        return self.value


@dataclass()
class Body(RequestField):
    type: str = field(default=RequestFieldType.BODY)


@dataclass()
class Query(RequestField):
    type: str = field(default=RequestFieldType.QUERY)


@dataclass()
class Header(RequestField):
    type: str = field(default=RequestFieldType.HEADER)


@dataclass()
class Placeholder(RequestField):
    type: str = field(default=RequestFieldType.PLACEHOLDER)


def request_field(
    field_type: RequestFieldType,
    field_factory: Optional[AnyValueFactory] = None,
    **pydantic_kwargs: Any,
) -> Any:
    if field_factory is not None:
        pydantic_kwargs.setdefault("default", None)
    data: dict[str, Any] = {"field_type": field_type, "field_factory": field_factory}
    return Field(
        json_schema_extra=data,
        **pydantic_kwargs,
    )  # type: ignore[pydantic-field]


def QueryField(  # noqa: N802
    field_factory: Optional[AnyValueFactory] = None,
    **pydantic_kwargs: Any,
) -> Any:
    return request_field(
        field_type=RequestFieldType.QUERY,
        field_factory=field_factory,
        **pydantic_kwargs,
    )


def BodyField(  # noqa: N802
    field_factory: Optional[AnyValueFactory] = None,
    **pydantic_kwargs: Any,
) -> Any:
    return request_field(
        field_type=RequestFieldType.BODY,
        field_factory=field_factory,
        **pydantic_kwargs,
    )


def HeaderField(  # noqa: N802
    field_factory: Optional[AnyValueFactory] = None,
    **pydantic_kwargs: Any,
) -> Any:
    return request_field(
        field_type=RequestFieldType.HEADER,
        field_factory=field_factory,
        **pydantic_kwargs,
    )


def PlaceholderField(  # noqa: N802
    field_factory: Optional[AnyValueFactory] = None,
    **pydantic_kwargs: Any,
) -> Any:
    return request_field(
        field_type=RequestFieldType.PLACEHOLDER,
        field_factory=field_factory,
        **pydantic_kwargs,
    )
