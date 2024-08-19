from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from stollen import Stollen
from stollen.requests.fields import Header

from .exceptions import CryptomusError, InvalidMerchantUUIDError
from .signature_factory import SignatureFactory

if TYPE_CHECKING:
    from .types import BalanceResponse


class Cryptomus(Stollen):
    _merchant: Final[str]
    _api_key: Final[str]

    def __init__(self, merchant: str, api_key: str, **stollen_kwargs: Any) -> None:
        self._merchant = merchant
        self._api_key = api_key
        super().__init__(
            base_url="https://api.cryptomus.com/v1",
            global_request_fields=[Header(name="merchant", value=merchant), SignatureFactory()],
            response_data_key=["result"],
            error_message_key=["message"],
            general_error_class=CryptomusError,
            error_codes={401: InvalidMerchantUUIDError},
            **stollen_kwargs,
        )

    @property
    def merchant(self) -> str:
        return self._merchant

    @property
    def api_key(self) -> str:
        return self._api_key

    async def get_balance(self) -> list[BalanceResponse]:
        from .methods import GetBalance

        call: GetBalance = GetBalance()
        return await self(call)
