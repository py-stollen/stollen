from pydantic import BaseModel, ConfigDict

from .client import StollenClientT
from .client.context_controller import StollenContextController


class StollenObject(StollenContextController[StollenClientT], BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
        extra="allow",
        validate_assignment=True,
        frozen=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
        defer_build=True,
    )


class MutableStollenObject(StollenObject[StollenClientT]):
    model_config = ConfigDict(frozen=False)
