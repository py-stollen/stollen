import json
from typing import Any

from .requests import StollenRequest, StollenResponse
from .utils.text import serialize_model


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


class DetailedStollenAPIError(StollenAPIError):
    def __init__(
        self,
        *,
        message: str = "An error has occurred during the request.",
        request: StollenRequest,
        response: StollenResponse,
        stringify: bool = True,
        **kwargs: Any,
    ) -> None:
        self.stringify = stringify
        super().__init__(message=message, request=request, response=response, **kwargs)

    def __str__(self) -> str:
        if not self.stringify:
            return json.dumps(
                {
                    "request": self.request.model_dump(),
                    "response": self.response.model_dump(),
                },
                default=str,
                ensure_ascii=False,
            )
        return (
            f"{self.message}\n"
            f"Request data:\n"
            f"{serialize_model(self.request)}\n"
            f"Response data:\n"
            f"{serialize_model(self.response)}"
        )
