from stollen.exceptions import StollenAPIError


class CryptomusError(StollenAPIError):
    pass


class InvalidMerchantUUIDError(StollenAPIError):
    pass
