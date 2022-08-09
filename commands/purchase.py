from copy import deepcopy

from utils.faker import fake
from utils.transport import get

from commands.base import Command


class PurchaseSpec(object):
    def __init__(self, **kwargs):
        self.product_id = kwargs.get('product_id')
        self.item_names = kwargs.get('items', '').split(',')
        self.params = kwargs.get('params', ['param_a', 'param_b'])
        self.marketplace_id = kwargs.get('marketplace_id')
        self.connection_id = kwargs.get('connection_id')
        self.customer = kwargs.get('tiers', {}).get('customer')
        self.tier1 = kwargs.get('tiers', {}).get('tier1')
        self.tier2 = kwargs.get('tiers', {}).get('tier2')

        self.product_version = None


class Purchase(Command):
    def __call__(self, api_base, token, requests_number, **kwargs):
        purchase_data = PurchaseSpec(**kwargs)
        post_tasks = build_post_tasks(api_base, requests_number, purchase_data, token)
        self._launch(token, post_tasks)


def tier_body(uuid=None):
    return {
        'name': fake.company(),
        'external_uid': uuid if uuid else fake.uuid4(),
        'tax_id': 'VAT-123',
        'contact_info': {
            'address_line1': '35 Sunset boulevard',
            'address_line2': '35 Sunset boulevard',
            'city': 'Bakersfield',
            'state': 'ca',
            'postal_code': '77100',
            'country': 'us',
            'contact': {
                'first_name': 'John',
                'last_name': 'Suhr',
                'email': 'j.suhr@example.com',
                'phone_number': {
                    'country_code': '+1',
                    'area_code': '040',
                    'phone_number': '2342479',
                    'extension': '2001',
                },
            },
        },
    }


def build_purchase_body(purchase_data: PurchaseSpec):
    item_names = purchase_data.item_names
    params = purchase_data.params

    tiers = {}
    if purchase_data.customer:
        tiers['customer'] = purchase_data.customer
    else:
        tiers['customer'] = tier_body()

    if purchase_data.tier1:
        tiers['tier1'] = purchase_data.tier1
    else:
        tiers['tier1'] = tier_body()

    if purchase_data.tier2:
        tiers['tier2'] = purchase_data.tier2

    data = {
        'type': 'purchase',
        'asset': {
            'external_id': str(fake.pyint()),
            'external_uid': fake.uuid4(),
            'product': {'id': purchase_data.product_id},
            'tiers': tiers,
        },
        'marketplace': {'id': purchase_data.marketplace_id},
    }
    if purchase_data.connection_id:
        data['asset']['connection'] = {'id': purchase_data.connection_id}
    else:
        data['asset']['connection'] = {'id': 'CT-0000-0000-0000', 'type': 'production'}

    data['asset']['items'] = [{'id': item, 'quantity': fake.pyint()} for item in item_names]
    data['asset']['params'] = [{'id': param, 'value': fake.word()} for param in params]

    return data


def prepare_purchase_spec(initial: PurchaseSpec, api_base: str, token: str):
    refined = deepcopy(initial)

    if not initial.product_id:
        resp_body = get(
            f"{api_base}/products?"
            "ordering(-name)"
            "&(((visibility.listing=true)|(visibility.syndication=true)))"
            "&limit=1&offset=0",
            token,
        )

        if resp_body:
            product = resp_body[0]
            refined.product_id = product['id']
            refined.product_version = product['version']

    if initial.item_names == ['']:
        resp_body = get(
            f"{api_base}/products/{refined.product_id}/versions/{refined.product_version}/items",
            token,
        )
        refined.item_names = [item['id'] for item in resp_body]

    if initial.params == ['param_a', 'param_b']:
        resp_body = get(
            f"{api_base}/products/{refined.product_id}/parameters?limit=1000&offset=0",
            token,
        )
        refined.params = [
            param['name']
            for param in resp_body
            if param['constraints']['required'] and param['scope'] == 'asset'
        ]

    if not initial.marketplace_id:
        resp_body = get(
            f"{api_base}/listings?"
            "ordering(-created)&limit=10&offset=0"
            f"&product__id={refined.product_id}",
            token,
        )
        if resp_body:
            listing = resp_body[0]
            refined.marketplace_id = listing['contract']['marketplace']['id']

    if not initial.connection_id:
        resp_body = get(f"{api_base}/products/{refined.product_id}/connections", token)
        if resp_body:
            refined.connection_id = resp_body[0]['id']

    return refined


def build_post_tasks(api_base: str, req_num: int, purchase_data: PurchaseSpec, token: str):
    ff_url = f"{api_base}/requests"
    refined_data = prepare_purchase_spec(purchase_data, api_base, token)
    return [(ff_url, build_purchase_body(refined_data)) for _ in range(req_num)]


def setup_purchase_command(arg_subparsers):
    purchase_parser = arg_subparsers.add_parser('purchase', help='Creates purchase requests')
    purchase_parser.add_argument(
        "-p", "--product-id", dest='product_id', type=str,
        help='ID of a product for subscriptions, example: PRD-001-000-002',
    )
    purchase_parser.add_argument(
        "-i", "--items", type=str,
        help='list of items IDs, example: "PRD-001-000-002-0001","PRD-001-000-002-0002"',
    )
    purchase_parser.add_argument(
        "-m", "--marketplace-id", dest='marketplace_id', type=str,
        help='ID of a marketplace where subscriptions are ordered, example: MP-55005'
    )
    purchase_parser.add_argument(
        "-C", "--connection-id", dest='connection_id', type=str,
        help='ID of a connection to hub where a target product is listed to.',
    )
    purchase = Purchase()
    purchase_parser.set_defaults(func=purchase)
