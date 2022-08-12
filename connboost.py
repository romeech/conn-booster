#!/usr/bin/env python
import argparse
import copy
import logging
import sys
import json

from commands.purchase import setup_purchase_command
from commands.tar import setup_tar_command


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
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        config = {}
    return config


def noop_fn(api_base, token, requests_number, **kwargs):
    print('No execution function is specified. Nothing to do')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--api-base", dest='api_base', type=str)
    parser.add_argument("-n", "--req-num", dest='req_num', type=int, default=10)
    parser.add_argument("-t", "--token", type=str)
    parser.add_argument("-c", "--config", type=str)

    subs = parser.add_subparsers(help="commands")

    for setup_command in (setup_purchase_command, setup_tar_command):
        setup_command(subs)

    args = parser.parse_args()
    passed_args = copy.deepcopy(args.__dict__)
    config = read_config(passed_args.pop('config', None) or CONFIG_PATH)

    # separate common args from a subcommand ones
    api_base = passed_args.pop('api_base') or config.get('api_base', DEFAULT_API_BASE)
    token = passed_args.pop('token') or config.get('token')
    req_num = passed_args.pop('req_num')

    command_fn = passed_args.pop('func', noop_fn)

    cmd_name = type(command_fn).__name__.split('.')[-1].lower()
    command_config = config.get(cmd_name, {})
    command_config.update({k: v for k, v in passed_args.items() if k in command_config and bool(v)})

    command_fn(api_base, token, req_num, **command_config)
