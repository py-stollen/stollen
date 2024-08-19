from __future__ import annotations

from typing import TYPE_CHECKING, Any

from stollen import Stollen
from stollen.requests.fields import Header

from .exceptions import UnknownAPIKeyError, XRocketError

if TYPE_CHECKING:
    from .types import AppInfo


class XRocket(Stollen):
    def __init__(self, pay_key: str, production: bool = True, **stollen_kwargs: Any) -> None:
        super().__init__(
            base_url="https://{subdomain}.ton-rocket.com",
            global_request_fields=[
                Header(name="Rocket-Pay-Key", value=pay_key),
                Header(name="Content-Type", value="application/json"),
            ],
            response_data_key=["data"],
            error_message_key=["message"],
            general_error_class=XRocketError,
            error_codes={403: UnknownAPIKeyError},
            default_subdomain="pay" if production else "dev-pay",
            **stollen_kwargs,
        )

    async def get_app_info(self) -> AppInfo:
        from .methods import GetAppInfo

        call: GetAppInfo = GetAppInfo()
        return await self(call)
