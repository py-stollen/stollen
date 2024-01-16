from pydantic import Field

from stollen import StollenObject

from ..client import XRocket
from .balance import Balance


class AppInfo(StollenObject[XRocket]):
    name: str
    fee_percents: float = Field(alias="feePercents")
    balances: list[Balance]
