import json
from typing import Any

from .requests.types import StollenRequest, StollenResponse


class StollenError(Exception):
    message: str

    def __init__(self, message: str, **kwargs: Any) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class StollenAPIError(StollenError):
    request: StollenRequest
    response: StollenResponse

    def __init__(
        self,
        message: str,
        request: StollenRequest,
        response: StollenResponse,
        **kwargs: Any,
    ) -> None:
        self.request = request
        self.response = response
        super().__init__(message=message, **kwargs)

    def __str__(self) -> str:
        return f"[{self.response.status_code}] {self.message}"


class DetailedStollenAPIError(StollenError):
    def __init__(
        self,
        *,
        message: str = "An error has occurred during the request.",
        request: StollenRequest,
        response: StollenResponse,
        stringify: bool = True,
        **kwargs: Any,
    ) -> None:
        self.request = request
        self.response = response
        if not stringify:
            message = f"{message}\nRequest data: {request}\nResponse data: {response}"
            super().__init__(message=message)
            return

        request_data: str = "\n".join(
            [
                f"  {field}={json.dumps(value, indent=4)}"
                for field, value in request.model_dump().items()
            ]
        )

        response_data: str = "\n".join(
            [
                f"  {field}={json.dumps(value, indent=4)}"
                for field, value in response.model_dump().items()
            ]
        )

        super().__init__(
            message=(
                f"{message}\n"
                f"Request data:\n"
                f"{request_data}\n"
                f"Response data:\n"
                f"{response_data}"
            ),
            **kwargs,
        )
