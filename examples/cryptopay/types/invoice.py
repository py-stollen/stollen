from datetime import datetime
from typing import Optional

from pydantic import Field

from stollen import StollenObject

from ..client import Cryptopay


class Invoice(StollenObject[Cryptopay]):
    id: int = Field(alias="invoice_id")
    hash: str
    currency_type: str
    asset: Optional[str] = None
    fiat: Optional[str] = None
    amount: float
    paid_asset: Optional[str] = None
    paid_amount: Optional[float] = None
    paid_fiat_rate: Optional[str] = None
    accepted_assets: Optional[list[str]] = None
    fee_asset: Optional[str] = None
    fee_amount: Optional[float] = None
    bot_invoice_url: str
    pay_url: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    paid_usd_rate: Optional[float] = None
    usd_rate: Optional[float] = None
    allow_comments: bool
    allow_anonymous: bool
    expiration_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    paid_anonymously: Optional[bool] = None
    comment: Optional[str] = None
    hidden_message: Optional[str] = None
    payload: Optional[str] = None
    paid_btn_name: Optional[str] = None
    paid_btn_url: Optional[str] = None
    mini_app_invoice_url: str
    web_app_invoice_url: str
