from dataclasses import dataclass, field

from ...enums import AccessNodeType


@dataclass()
class APIAccessNode:
    name: str
    value: str | int
    type: str


@dataclass()
class URLPlaceholder(APIAccessNode):
    type: str = field(default=AccessNodeType.URL_PLACEHOLDER)


@dataclass()
class Header(APIAccessNode):
    type: str = field(default=AccessNodeType.HEADER)
