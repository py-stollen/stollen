from stollen import StollenMethod
from stollen.enums import HTTPMethod
from stollen.types import StollenT

from ..client import TelegramBot


class TelegramMethod(
    StollenMethod[StollenT, TelegramBot],
    http_method=HTTPMethod.POST,
    abstract=True,
):
    pass
