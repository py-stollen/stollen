from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, TypeAlias

from ..client import Stollen
from ..method import StollenMethod
from .fields import RequestField

RequestFieldFactory: TypeAlias = Callable[
    [Stollen, StollenMethod[Any, Stollen]],
    RequestField | Iterable[RequestField],
]


class BaseRequestFieldFactory(ABC):
    @abstractmethod
    def __call__(
        self,
        client: Stollen,
        method: StollenMethod[Any, Stollen],
    ) -> Iterable[RequestField] | RequestField:
        pass
