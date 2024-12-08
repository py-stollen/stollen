import xmltodict

from stollen import Stollen, StollenMethod
from stollen.client import StollenClientT
from stollen.requests import RequestSerializer, StollenRequest
from stollen.types import StollenT


class XMLSerializer(RequestSerializer):
    def to_request(
        self,
        client: Stollen,
        method: StollenMethod[StollenT, StollenClientT],
    ) -> StollenRequest:
        request: StollenRequest = super().to_request(client, method)
        if request.body:
            request.headers["Content-Type"] = "application/xml; charset=utf-8"
            request.body = xmltodict.unparse(request.body)
        return request
