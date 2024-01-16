from stollen.exceptions import StollenAPIError


class CryptopayError(StollenAPIError):
    pass


class UnauthorizedError(CryptopayError):
    pass
