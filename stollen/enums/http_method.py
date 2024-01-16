from enum import StrEnum


class HTTPMethod(StrEnum):
    HEAD = "HEAD"
    GET = "GET"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"
