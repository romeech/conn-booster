#! /Users/romeech/projects/python/conn-booster/venv/bin/python

import argparse
import asyncio
import copy
import logging
import sys
import json

from aiohttp import ClientSession

from tasks.purchase import setup_commmand_parser
from tasks.tar import build_tar_tasks


DEFAULT_API_BASE = 'https://api.cnct.info/public/v1'
CONFIG_PATH = 'config.json'


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("async_requests")
logging.getLogger("chardet.charsetprober").disabled = True


def read_config(path):
    try:
        config = json.load(open(path, 'r'))
    except json.decoder.JSONDecodeError:
        config = {}
    return config


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


def send_tars_f(args):
    config = read_config()
    args = args.__dict__
    config.update(args)

    api_base = args.get('api_base', DEFAULT_API_BASE)
    ta_id = args['ta_id']
    ta_uid = args['ta_uid']
    token = args['token']
    req_num = args['req_num']

    post_tasks = build_tar_tasks(api_base, req_num, ta_id, ta_uid)
    asyncio.run(launch_requests(token, post_tasks))


def send_products_f(args):
    pass


def noop_fn(api_base, token, requests_number, **kwargs):
    print('No execution function is specified. Nothing to do')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api-base", dest='api_base', type=str)
    parser.add_argument("-n", "--req-num", dest='req_num', type=int, default=10)
    parser.add_argument("-t", "--token", type=str)
    parser.add_argument("-c", "--config", type=str)

    subs = parser.add_subparsers(help="commands")

    setup_commmand_parser(subs)

    # TODO: subparser for 'product'
    # product_parser = subs.add_parser('product', help='Creates products')
    # product_parser.set_defaults(send_products_f)

    tar_parser = subs.add_parser('tar', help='Creates tier account requests')
    tar_parser.add_argument("--ta-id", dest='ta_id', type=str)
    tar_parser.add_argument("--ta-uid", dest='ta_uid', type=str)
    tar_parser.set_defaults(func=send_tars_f)

    args = parser.parse_args()
    passed_args = copy.deepcopy(args.__dict__)
    config = read_config(passed_args.pop('config', None) or CONFIG_PATH)

    breakpoint()
    # separate common args from a subcommand ones
    api_base = passed_args.pop('api_base') or config.get('api_base', DEFAULT_API_BASE)
    token = passed_args.pop('token') or config.get('token')
    req_num = passed_args.pop('req_num')

    command_fn = passed_args.pop('func', noop_fn)

    command_config = config.get(command_fn.__name__, {})
    command_config.update({k: v for k, v in passed_args.items() if k in command_config and bool(v)})

    breakpoint()
    command_fn(api_base, token, req_num, **command_config)


# import asyncio
# import uvloop

# async def main():
#     # Main entry-point.
#     ...

# uvloop.install()
# asyncio.run(launch_requests())
