from __future__ import annotations

from enum import Enum, auto

from .http_method import HTTPMethod


class RequestFieldType(str, Enum):
    AUTO = auto()
    BODY = auto()
    QUERY = auto()
    HEADER = auto()
    PLACEHOLDER = auto()
    FILE = auto()

    @classmethod
    def resolve(cls, http_method: str) -> RequestFieldType:
        if http_method in {HTTPMethod.GET, HTTPMethod.HEAD, HTTPMethod.OPTIONS, HTTPMethod.TRACE}:
            return RequestFieldType.QUERY
        if http_method in {HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH, HTTPMethod.DELETE}:
            return RequestFieldType.BODY
        raise ValueError(f"Unknown HTTP method: {http_method}")
