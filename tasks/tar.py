from utils.faker import fake


def build_tar_body(ta_id=None, ta_uid=None, **kwargs):
    account_body = {}
    if ta_id:
        account_body['id'] = ta_id
    if ta_uid:
        account_body['external_uid'] = ta_uid
    if kwargs.get('name'):
        account_body['name'] = kwargs['name']
    else:
        account_body['name'] = fake.company()

    return {
        'type': 'update',
        'account': account_body,
    }


def build_tar_tasks(api_base, req_num, ta_id, ta_uid, **kwargs):
    tar_url = f'{api_base}/tier/account-requests'

    return [(tar_url, build_tar_body(ta_id, ta_uid, **kwargs)) for _ in range(req_num)]
