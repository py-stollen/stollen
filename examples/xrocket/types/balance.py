from stollen import StollenObject

from ..client import XRocket


class Balance(StollenObject[XRocket]):
    currency: str
    balance: float
