import asyncio

from utils.transport import launch_requests


class Command(object):
    """Declares unified signature for commands and implements async launcher"""
    def __call__(self, api_base, token, requests_number, **kwargs):
        print('No execution function is specified. Nothing to do')

    def _launch(self, token, tasks):
        asyncio.run(launch_requests(token, tasks))
