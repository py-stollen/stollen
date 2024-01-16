from stollen import StollenObject

from ..client import Cryptomus
from .balance_unit import BalanceUnit


class Balance(StollenObject[Cryptomus]):
    merchant: list[BalanceUnit]
    user: list[BalanceUnit]
