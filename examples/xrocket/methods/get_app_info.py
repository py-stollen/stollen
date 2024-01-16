from stollen import StollenMethod
from stollen.enums import HTTPMethod

from ..client import XRocket
from ..types import AppInfo


class GetAppInfo(
    StollenMethod[AppInfo, XRocket],
    http_method=HTTPMethod.GET,
    api_method="/app/info",
    returning=AppInfo,
):
    pass
