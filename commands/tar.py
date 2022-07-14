from utils.faker import fake

from commands.base import Command


class TarSpec(object):
    def __init__(self, **kwargs):
        self.ta_id = kwargs['ta_id']
        self.ta_uid = kwargs['ta_uid']
        self.name = kwargs['name']


class Tar(Command):
    def __call__(self, api_base, token, requests_number, **kwargs):
        tar_data = TarSpec(**kwargs)
        post_tasks = build_tar_tasks(api_base, requests_number, tar_data)
        self._launch(token, post_tasks)


def build_tar_body(tar_data):
    account_body = {}
    if tar_data.ta_id:
        account_body['id'] = tar_data.ta_id
    if tar_data.ta_uid:
        account_body['external_uid'] = tar_data.ta_uid
    # generate changes
    account_body['name'] = tar_data.name if tar_data.name else fake.company()

    return {
        'type': 'update',
        'account': account_body,
    }


def build_tar_tasks(api_base, req_num, ta_id, ta_uid, **kwargs):
    tar_url = f'{api_base}/tier/account-requests'

    return [(tar_url, build_tar_body(ta_id, ta_uid, **kwargs)) for _ in range(req_num)]


def setup_tar_command(arg_subparsers):
    tar_parser = arg_subparsers.add_parser('tar', help='Creates tier account requests')
    tar_parser.add_argument("--ta-id", dest='ta_id', type=str)
    tar_parser.add_argument("--ta-uid", dest='ta_uid', type=str)
    tar = Tar()
    tar_parser.set_defaults(func=tar)
