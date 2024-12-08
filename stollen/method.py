from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Generator, Generic, Optional, Union

from pydantic import BaseModel, ConfigDict, TypeAdapter

from .client import StollenClientT
from .client.context_controller import StollenContextController
from .const import DEFAULT_CHUNK_SIZE
from .enums import HTTPMethod, RequestFieldType
from .requests import FileResponse
from .types import StollenT

if TYPE_CHECKING:
    from .types import HTTPMethodType


class StollenMethod(
    StollenContextController[StollenClientT],
    BaseModel,
    Generic[StollenT, StollenClientT],
):
    subdomain: ClassVar[Optional[str]]
    http_method: ClassVar[Union[HTTPMethod, HTTPMethodType]]
    api_method: ClassVar[str]
    returning: ClassVar[type[Any]]
    response_data_key: ClassVar[list[str]]
    default_field_type: ClassVar[RequestFieldType]
    type_adapter: ClassVar[TypeAdapter[Any]]
    __abstract: ClassVar[bool] = False

    async def emit(self, client: StollenClientT) -> StollenT:
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
    def __validate_class_var(
        cls,
        name: str,
        kwargs: dict[str, Any],
        default: Optional[Any] = None,
        required: bool = True,
    ) -> None:
        var: Optional[Any] = kwargs.pop(name, default)
        if var is None and getattr(cls, name, None):
            return
        if required and var is None:
            msg: str = f"Missing `{name}` parameter while declaring `{cls.__name__}` method!"
            raise TypeError(msg)
        setattr(cls, name, var)

    @classmethod
    def __resolve_abstract(cls, kwargs: dict[str, Any]) -> None:
        cls.__abstract = kwargs.pop("abstract", None) or getattr(cls, "__abstract", False)
        mro: list[type[Any]] = list(cls.__mro__)
        parent: type[Any] = mro[mro.index(cls) + 1]
        if cls.__name__.startswith(f"{parent.__name__}[") and issubclass(parent, StollenMethod):
            cls.__abstract = parent.__abstract

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, **kwargs: Any) -> None:  # type: ignore
        cls.__resolve_abstract(kwargs)
        # Prevent class var validation for the Generic class
        if not getattr(cls, "__parameters__", None):
            var_required: bool = not cls.__abstract
            cls.__validate_class_var(name="subdomain", kwargs=kwargs, required=False)
            cls.__validate_class_var(name="http_method", kwargs=kwargs, required=var_required)
            cls.__validate_class_var(name="api_method", kwargs=kwargs, required=var_required)
            cls.__validate_class_var(name="returning", kwargs=kwargs, required=var_required)
            cls.__validate_class_var(name="response_data_key", kwargs=kwargs, default=[])
            cls.__validate_class_var(
                name="default_field_type",
                kwargs=kwargs,
                default=RequestFieldType.AUTO,
            )
            if getattr(cls, "returning", None):
                cls.type_adapter = TypeAdapter[StollenT](cls.returning)
            # Set extra class vars if needed
            for name in kwargs.copy():
                if name in cls.__class_vars__:
                    setattr(cls, name, kwargs.pop(name))
        super().__init_subclass__(**kwargs)

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )


class StollenStreamingMethod(
    StollenMethod[FileResponse, StollenClientT],
    returning=FileResponse,
    abstract=True,
):
    """
    Abstract class for methods with streaming response
    """

    chunk_size: ClassVar[int] = DEFAULT_CHUNK_SIZE
