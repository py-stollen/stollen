from __future__ import annotations

import logging

from stollen import Stollen, StollenMethod, StollenObject
from stollen.enums import HTTPMethod

from .serializer import XMLSerializer
from .session import XMLValidatorSession


class Pong(StollenObject[Stollen]):
    success: bool


class Ping(
    StollenMethod[Pong, Stollen],
    http_method=HTTPMethod.POST,
    api_method="/ping",
    returning=Pong,
):
    tries: int


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)
    session: XMLValidatorSession = XMLValidatorSession(serializer=XMLSerializer())
    stollen: Stollen = Stollen(base_url="https://api.example.com", session=session)
    logging.info(session.serializer.to_request(stollen, Ping(tries=2)))


if __name__ == "__main__":
    main()
