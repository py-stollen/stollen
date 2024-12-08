from __future__ import annotations

import asyncio
import logging
from typing import Any

from stollen import Stollen, StollenMethod, StollenObject
from stollen.enums import HTTPMethod
from stollen.exceptions import StollenAPIError


class CoingeckoAPIError(StollenAPIError):
    pass


class RateLimitError(CoingeckoAPIError):
    pass


class Coingecko(Stollen):
    def __init__(self, **stollen_kwargs: Any) -> None:
        super().__init__(
            base_url="https://api.coingecko.com/api/v3",
            error_message_key=["status", "error_message"],
            general_error_class=CoingeckoAPIError,
            error_codes={429: RateLimitError},
            stringify_detailed_errors=False,
            **stollen_kwargs,
        )

    async def ping(self) -> GeckoSays:
        call: Ping = Ping()
        return await self(call)


class GeckoSays(StollenObject[Coingecko]):
    gecko_says: str


class Ping(
    StollenMethod[GeckoSays, Coingecko],
    http_method=HTTPMethod.GET,
    api_method="/ping",
    returning=GeckoSays,
):
    pass


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    async with Coingecko() as coingecko:
        gecko_says: GeckoSays = await coingecko.ping()
        logging.info(gecko_says)


if __name__ == "__main__":
    asyncio.run(main())
