from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generator, Generic, Optional

from pydantic import BaseModel, TypeAdapter

from . import Stollen
from .client import StollenClientT
from .client.context_controller import StollenContextController
from .types import StollenT

if TYPE_CHECKING:
    from .types import HTTPMethodType


class StollenMethod(
    StollenContextController[StollenClientT], BaseModel, Generic[StollenT, StollenClientT]
):
    http_method: ClassVar[HTTPMethodType]
    api_method: ClassVar[str]
    returning: ClassVar[type[Any]]
    type_adapter: ClassVar[TypeAdapter[Any]]

    async def emit(self, client: Stollen) -> StollenT:
        return await client(self)

    def __await__(self) -> Generator[Any, None, StollenT]:
        client: Optional[StollenClientT] = self._client
        if not client:
            raise RuntimeError(
                "This method is not mounted to an any stollen instance, "
                "please call it explicitly with stollen instance `await stollen(method)`\n"
                "or mount method to a stollen instance `method.as_(stollen)` "
                "and then call it `await method()`"
            )
        return self.emit(client).__await__()

    @classmethod
    def __validate_class_var(cls, name: str, kwargs: dict[str, Any]) -> None:
        var: Optional[Any] = kwargs.pop(name, None)
        if var is None:
            raise TypeError(f"Missing `{name}` parameter while declaring `{cls.__name__}` method!")
        setattr(cls, name, var)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        # Prevent class var validation for the Generic class
        if not getattr(cls, "__parameters__", None):
            cls.__validate_class_var(name="http_method", kwargs=kwargs)
            cls.__validate_class_var(name="api_method", kwargs=kwargs)
            cls.__validate_class_var(name="returning", kwargs=kwargs)
            cls.type_adapter = TypeAdapter[StollenT](cls.returning)
        super().__init_subclass__(**kwargs)
