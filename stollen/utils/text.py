import json

from pydantic import BaseModel


def camel_to_snake(string: str) -> str:
    parts: list[str] = [f"{c.lower()}_" if c.isupper() else c for c in string]
    return "".join(parts).rstrip("_")


def serialize_model(model: BaseModel) -> str:
    return "\n".join(
        [
            f"  {field}={json.dumps(value, indent=4, default=lambda obj: str(obj))}"
            for field, value in model.model_dump().items()
        ]
    )
