from typing import Any, Callable, Literal, TypeVar

from typing_extensions import TypeAlias

StollenT = TypeVar("StollenT", bound=Any)

JsonLoads: TypeAlias = Callable[..., Any]
JsonDumps: TypeAlias = Callable[..., str]

HTTPMethodType: TypeAlias = Literal[
    "HEAD",
    "GET",
    "DELETE",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
    "TRACE",
]
