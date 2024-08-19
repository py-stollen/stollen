from __future__ import annotations

from base64 import b64encode
from hashlib import md5
from typing import Any

from stollen import Stollen, StollenMethod
from stollen.requests.factory import BaseRequestFieldFactory
from stollen.requests.fields import Header, RequestField


class SignatureFactory(BaseRequestFieldFactory):
    def __call__(
        self,
        client: Stollen,
        method: StollenMethod[Any, Stollen],
    ) -> RequestField:
        from .client import Cryptomus

        if not isinstance(client, Cryptomus):
            raise RuntimeError("Got an unexpected client type instance.")

        exclude_none: bool = client.session.exclude_none_in_methods
        data: dict[str, Any] = method.model_dump(exclude_none=exclude_none)
        raw_data: str = client.session.json_dumps(data) if data else ""
        sign_base: bytes = (b64encode(str.encode(raw_data)).decode() + client.api_key).encode()

        return Header(
            name="sign",
            value=md5(sign_base).hexdigest(),  # noqa: S324
        )
