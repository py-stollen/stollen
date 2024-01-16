from typing import Any, Iterable, Optional


def recursive_getitem(mapping: dict[str, Any], keys: Optional[Iterable[str]] = None) -> Any:
    if not keys:
        return mapping
    value: Any = mapping
    for key in keys:
        value = value[key]
    return value
