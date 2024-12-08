from __future__ import annotations

from typing import Any, Generic, Optional

from pydantic import BaseModel, PrivateAttr
from typing_extensions import Self

from .client import StollenClientT


class StollenContextController(BaseModel, Generic[StollenClientT]):
    _client: Optional[StollenClientT] = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        self._client = __context.get("client") if __context else None

    def as_(self, client: Optional[StollenClientT]) -> Self:
        """
        Bind object to a stollen instance.
        """
        self._client = client
        return self

    @property
    def client(self) -> Optional[StollenClientT]:
        return self._client
