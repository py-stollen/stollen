from decimal import Decimal

from stollen import StollenObject

from ..client import Cryptomus


class BalanceUnit(StollenObject[Cryptomus]):
    uuid: str
    balance: Decimal
    currency_code: str


class Balance(StollenObject[Cryptomus]):
    merchant: list[BalanceUnit]
    user: list[BalanceUnit]


class BalanceResponse(StollenObject[Cryptomus]):
    balance: Balance
