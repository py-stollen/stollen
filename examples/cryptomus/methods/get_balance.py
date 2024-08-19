from stollen import StollenMethod
from stollen.enums import HTTPMethod

from ..client import Cryptomus
from ..types import BalanceResponse


class GetBalance(
    StollenMethod[list[BalanceResponse], Cryptomus],
    http_method=HTTPMethod.POST,
    api_method="/balance",
    returning=list[BalanceResponse],
):
    pass
