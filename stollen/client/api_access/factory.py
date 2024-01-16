from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from ...method import StollenMethod
    from ...types import StollenT
    from ..client import StollenClientT
    from .nodes import APIAccessNode


class BaseAPIAccessNodeFactory(ABC):
    @abstractmethod
    def construct(
        self,
        *,
        client: StollenClientT,
        method: StollenMethod[StollenT, StollenClientT],
    ) -> Iterable[APIAccessNode]:
        pass
