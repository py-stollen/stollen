from typing import Optional

from stollen import StollenMethod
from stollen.enums import HTTPMethod

from ..client import Cryptopay
from ..types import Invoice


class CreateInvoice(
    StollenMethod[Invoice, Cryptopay],
    http_method=HTTPMethod.POST,
    api_method="/createInvoice",
    returning=Invoice,
):
    currency_type: Optional[str] = None
    asset: Optional[str] = None
    fiat: Optional[str] = None
    accepted_assets: Optional[str] = None
    amount: float
    description: Optional[str] = None
    hidden_message: Optional[str] = None
    paid_btn_name: Optional[str] = None
    paid_btn_url: Optional[str] = None
    payload: Optional[str] = None
    allow_comments: Optional[bool] = None
    allow_anonymous: Optional[bool] = None
    expires_in: Optional[int] = None
