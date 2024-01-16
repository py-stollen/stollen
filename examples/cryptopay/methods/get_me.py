from stollen import StollenMethod
from stollen.enums import HTTPMethod

from ..client import Cryptopay
from ..types import Profile


class GetMe(
    StollenMethod[Profile, Cryptopay],
    http_method=HTTPMethod.POST,
    api_method="/getMe",
    returning=Profile,
):
    pass
