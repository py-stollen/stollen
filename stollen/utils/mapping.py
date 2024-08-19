from typing import Any, Iterable, Optional


def recursive_getitem(mapping: Any, keys: Optional[Iterable[str]] = None) -> Any:
    if not isinstance(mapping, dict):
        return mapping
    if not keys:
        return mapping
    value: Any = mapping
    for key in keys:
        value = value[key]
    return value
