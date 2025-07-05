import ssl
from typing import Optional, Dict

import aiohttp
import certifi


def _get_connector_for_ssl() -> aiohttp.TCPConnector:
    """
    SSL 설정을 사용하여 안전한 TCPConnector를 반환
    """
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return aiohttp.TCPConnector(ssl=ssl_context)


async def _request_get_to(url, headers=None) -> Optional[Dict]:
    """
    비동기 GET 요청을 보내고 응답을 반환
    """
    conn = _get_connector_for_ssl()
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url, headers=headers) as resp:
            return None if resp.status != 200 else await resp.json()


async def _request_post_to(url, payload=None) -> Optional[Dict]:
    """
    비동기 POST 요청을 보내고 응답을 반환.
    """
    conn = _get_connector_for_ssl()
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.post(url, data=payload) as resp:
            return None if resp.status != 200 else await resp.json()
