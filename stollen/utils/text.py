import json
import re

from pydantic import BaseModel


def camel_to_snake(string: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", string).lower()


def serialize_model(model: BaseModel) -> str:
    return "\n".join(
        [
            f"  {field}={json.dumps(value, indent=4, default=lambda obj: str(obj))}"
            for field, value in model.model_dump().items()
        ]
    )
