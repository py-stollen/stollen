from stollen.exceptions import StollenAPIError


class XRocketError(StollenAPIError):
    pass


class UnknownAPIKeyError(XRocketError):
    pass
