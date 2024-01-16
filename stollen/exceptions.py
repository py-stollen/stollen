from typing import Any, Optional


class StollenError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class StollenAPIError(StollenError):
    code: int
    raw_response: Optional[dict[str, Any]]

    def __init__(
        self, message: str, code: int, raw_response: Optional[dict[str, Any]] = None
    ) -> None:
        self.code = code
        self.raw_response = raw_response
        super().__init__(message=message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
