import asyncio
import json
import logging

from aiohttp import ClientSession

from requests import Session
from requests.adapters import HTTPAdapter

from urllib3 import Retry


logger = logging.getLogger("async_requests")
logging.getLogger("chardet.charsetprober").disabled = True


async def post(session: ClientSession, url: str, token: str = None, **kwargs):
    kwargs['headers'] = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }
    resp = await session.request(method='POST', url=url, **kwargs)
    resp_body = await resp.json()
    logger.info("Got response [%s] for URL: %s, result: %s", resp.status, url, resp_body)
    return resp_body


def get(url: str, token: str = None):
    retry_on_statuses = [408, 429, 502, 503, 504]
    retry_on_methods = ['HEAD', 'OPTIONS', 'GET', 'POST', 'PUT', 'DELETE']
    retry_policy = Retry(
        total=3,
        status_forcelist=retry_on_statuses,
        allowed_methods=retry_on_methods,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_policy)

    session = Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers = {
        'Authorization': token,
        'Content-Type': 'application/json',
    }

    response = session.get(url)

    response.raise_for_status()

    return response.json()


async def launch_requests(token, post_tasks):
    async with ClientSession() as session:
        requests = []
        requests = [post(session, url, token, data=json.dumps(body)) for url, body in post_tasks]
        results = await asyncio.gather(*requests)
        return results
