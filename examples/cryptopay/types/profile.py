from stollen import StollenObject

from ..client import Cryptopay


class Profile(StollenObject[Cryptopay]):
    app_id: int
    name: str
    payment_processing_bot_username: str
