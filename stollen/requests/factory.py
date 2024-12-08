from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, Optional, Union

from typing_extensions import TypeAlias

from ..client import Stollen
from ..method import StollenMethod
from .fields import RequestField

RequestFieldFactory: TypeAlias = Callable[
    [Stollen, StollenMethod[Any, Stollen]],
    Optional[Union[RequestField, Iterable[RequestField]]],
]

AnyValueFactory: TypeAlias = Callable[
    [Stollen, StollenMethod[Any, Stollen]],
    Any,
]


class BaseRequestFieldFactory(ABC):
    @abstractmethod
    def __call__(
        self,
        client: Stollen,
        method: StollenMethod[Any, Stollen],
    ) -> Union[Iterable[RequestField], RequestField]:
        pass
