from typing import Any, Iterable, Optional, Union, cast

from aiohttp import BasicAuth, TCPConnector

ProxyBasic = Union[str, tuple[str, BasicAuth]]
ProxyChain = Iterable[ProxyBasic]
ProxyType = Union[ProxyChain, ProxyBasic]


def retrieve_basic(basic: ProxyBasic) -> dict[str, Any]:
    from aiohttp_socks.utils import parse_proxy_url  # type: ignore

    proxy_auth: Optional[BasicAuth] = None

    if isinstance(basic, str):
        proxy_url = basic
    else:
        proxy_url, proxy_auth = basic

    proxy_type, host, port, username, password = parse_proxy_url(proxy_url)
    if isinstance(proxy_auth, BasicAuth):
        username = proxy_auth.login
        password = proxy_auth.password

    return {
        "proxy_type": proxy_type,
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "rdns": True,
    }


def prepare_connector(chain_or_plain: ProxyType) -> tuple[type[TCPConnector], dict[str, Any]]:
    from aiohttp_socks import (  # type: ignore
        ChainProxyConnector,
        ProxyConnector,
        ProxyInfo,
    )

    # since tuple is Iterable(compatible with ProxyChain) object, we assume that
    # user wants chained proxies if tuple is a pair of string(url) and BasicAuth
    if isinstance(chain_or_plain, str) or (
        isinstance(chain_or_plain, tuple) and len(chain_or_plain) == 2
    ):
        chain_or_plain = cast(ProxyBasic, chain_or_plain)
        return ProxyConnector, retrieve_basic(chain_or_plain)

    chain_or_plain = cast(ProxyChain, chain_or_plain)
    infos: list[ProxyInfo] = []
    for basic in chain_or_plain:
        infos.append(ProxyInfo(**retrieve_basic(basic)))

    return ChainProxyConnector, {"proxy_infos": infos}
