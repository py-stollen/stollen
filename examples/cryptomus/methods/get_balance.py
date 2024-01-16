from stollen import StollenMethod
from stollen.enums import HTTPMethod

from ..client import Cryptomus
from ..types import Balance


class GetBalance(
    StollenMethod[list[Balance], Cryptomus],
    http_method=HTTPMethod.POST,
    api_method="/balance",
    returning=list[Balance],
):
    pass
