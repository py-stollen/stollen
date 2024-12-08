
#######
stollen
#######

.. image:: https://img.shields.io/pypi/l/stollen.svg?style=flat-square
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

.. image:: https://img.shields.io/pypi/status/stollen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/stollen
    :alt: PyPi status

.. image:: https://img.shields.io/pypi/v/stollen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/stollen
    :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/dm/stollen.svg?style=flat-square
    :target: https://pypistats.org/packages/stollen
    :alt: Downloads

.. image:: https://img.shields.io/pypi/pyversions/stollen.svg?style=flat-square
    :target: https://pypi.python.org/pypi/stollen
    :alt: Supported python versions

**Stollen** is an asynchronous framework designed to streamline the process
of building API clients, written in Python 3.9+ using
`aiohttp <https://github.com/aio-libs/aiohttp>`_ and
`pydantic <https://docs.pydantic.dev/latest/>`_.
With a declarative approach, Stollen allows developers
to define API methods, handle responses, and manage errors
in a structured way, focusing on clarity and scalability.

Installation
------------

..  code-block:: bash

    pip install -U stollen

Example
-------

.. code-block:: python

    from __future__ import annotations

    import asyncio
    import logging

    from stollen import Stollen, StollenMethod, StollenObject
    from stollen.enums import HTTPMethod
    from stollen.exceptions import StollenAPIError


    class CoingeckoAPIError(StollenAPIError):
        pass


    class RateLimitError(CoingeckoAPIError):
        pass


    class Coingecko(Stollen):
        def __init__(self) -> None:
            super().__init__(
                base_url="https://api.coingecko.com/api/v3",
                error_message_key=["status", "error_message"],
                general_error_class=CoingeckoAPIError,
                error_codes={429: RateLimitError},
                stringify_detailed_errors=False,
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
