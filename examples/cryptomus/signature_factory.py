from __future__ import annotations

from base64 import b64encode
from hashlib import md5
from typing import Iterable

from stollen import StollenMethod
from stollen.client import StollenClientT
from stollen.client.api_access import APIAccessNode, BaseAPIAccessNodeFactory, Header
from stollen.types import StollenT


class SignatureFactory(BaseAPIAccessNodeFactory):
    def construct(
        self,
        *,
        client: StollenClientT,
        method: StollenMethod[StollenT, StollenClientT],
    ) -> Iterable[APIAccessNode]:
        from .client import Cryptomus

        if not isinstance(client, Cryptomus):
            raise RuntimeError("Got an unexpected client type instance.")

        json_data: str = client.session.json_dumps(
            method.model_dump(
                by_alias=client.session.use_dump_aliases,
                exclude_none=client.session.exclude_none_in_methods,
            )
        )
        sign_base: bytes = str.encode(json_data + client.api_key)

        return [
            Header(
                name="sign",
                value=md5(b64encode(sign_base)).hexdigest(),  # noqa: S324
            )
        ]
