from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from stollen import Stollen
from stollen.requests.fields import Header

from .exceptions import CryptopayError, UnauthorizedError

if TYPE_CHECKING:
    from .types import Invoice, Profile


class Cryptopay(Stollen):
    def __init__(self, api_token: str, production: bool = True, **stollen_kwargs: Any) -> None:
        host: str = "pay.crypt.bot" if production else "testnet-pay.crypt.bot"
        super().__init__(
            base_url=f"https://{host}/api",
            global_request_fields=[
                Header(name="Host", value=host),
                Header(name="Crypto-Pay-API-Token", value=api_token),
            ],
            response_data_key=["result"],
            error_message_key=["error", "name"],
            general_error_class=CryptopayError,
            error_codes={401: UnauthorizedError},
            **stollen_kwargs,
        )

    async def get_me(self) -> Profile:
        from .methods import GetMe

        call: GetMe = GetMe()
        return await self(call)

    async def create_invoice(
        self,
        *,
        currency_type: Optional[str] = None,
        asset: Optional[str] = None,
        fiat: Optional[str] = None,
        accepted_assets: Optional[str] = None,
        amount: float,
        description: Optional[str] = None,
        hidden_message: Optional[str] = None,
        paid_btn_name: Optional[str] = None,
        paid_btn_url: Optional[str] = None,
        payload: Optional[str] = None,
        allow_comments: Optional[bool] = None,
        allow_anonymous: Optional[bool] = None,
        expires_in: Optional[int] = None,
    ) -> Invoice:
        from .methods import CreateInvoice

        call: CreateInvoice = CreateInvoice(
            currency_type=currency_type,
            asset=asset,
            fiat=fiat,
            accepted_assets=accepted_assets,
            amount=amount,
            description=description,
            hidden_message=hidden_message,
            paid_btn_name=paid_btn_name,
            paid_btn_url=paid_btn_url,
            payload=payload,
            allow_comments=allow_comments,
            allow_anonymous=allow_anonymous,
            expires_in=expires_in,
        )
        return await self(call)
