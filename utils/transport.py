import asyncio
import json
import logging

from aiohttp import ClientSession


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


async def launch_requests(token, post_tasks):
    async with ClientSession() as session:
        requests = []
        requests = [post(session, url, token, data=json.dumps(body)) for url, body in post_tasks]
        results = await asyncio.gather(*requests)
        return results
