from typing import Any

import xmltodict

from stollen import Stollen
from stollen.requests import StollenRequest, StollenResponse
from stollen.session.aiohttp import AiohttpSession


class XMLValidatorSession(AiohttpSession):
    @classmethod
    def prepare_response(
        cls,
        client: Stollen,
        request: StollenRequest,
        response: StollenResponse,
    ) -> Any:
        if isinstance(response.body, (str, bytes)):
            response.body = xmltodict.parse(response.body)
        return super().prepare_response(client, request, response)
