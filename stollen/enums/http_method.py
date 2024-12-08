from enum import Enum


class HTTPMethod(str, Enum):
    HEAD = "HEAD"
    GET = "GET"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"
    TRACE = "TRACE"
