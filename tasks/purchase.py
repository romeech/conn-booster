import copy
import asyncio

from utils.faker import fake
from utils.transport import launch_requests


def build_purchase_body(**kwargs):
    connection_id = kwargs.get('connection_id')
    product_id = kwargs.get('product_id', 'PRD-045-208-643')
    item_names = kwargs.get('item_names', [
        'PRD-045-208-643-0001', 'PRD-045-208-643-0002', 'PRD-045-208-643-0003',
    ])
    params = kwargs.get('params', ['param_a', 'param_b'])
    marketplace_id = kwargs.get('marketplace_id', 'MP-55005')
    customer_uid = kwargs.get('customer_uid', fake.uuid4())
    tier1_uid = kwargs.get('tier1_uid', fake.uuid4())

    customer_body = {
        'name': fake.company(),
        'external_uid': customer_uid,
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
    customer_body = {'id': "TA-3279-6101-1009"}

    tier1_body = copy.deepcopy(customer_body)
    tier1_body['external_uid'] = tier1_uid
    tier1_body['name'] = 'Reseller Inc'
    # tier1_body['name'] = fake.company()
    tier1_body = {'id': 'TA-1042-3334-8462'}

    data = {
        'type': 'purchase',
        'asset': {
            'external_id': str(fake.pyint()),
            'external_uid': fake.uuid4(),
            'product': {'id': product_id},
            'tiers': {
                'customer': customer_body,
                'tier1': tier1_body,
            },
        },
        'marketplace': {'id': marketplace_id},
    }
    if connection_id:
        data['asset']['connection'] = {'id': connection_id}
    else:
        data['asset']['connection'] = {'id': 'CT-0000-0000-0000', 'type': 'production'}

    data['asset']['items'] = [{'id': item, 'quantity': fake.pyint()} for item in item_names]
    data['asset']['params'] = [{'id': param, 'value': fake.word()} for param in params]

    return data


def build_post_tasks(
    api_base, product_id, item_names, marketplace_id,
    req_num=5,
    customer_uid=None,
    tier1_uid='247f47a0-6e3b-4eaf-9025-98656b18f3c5',
    tier2_uid=None,
    connection_id='CT-6821-6299',
):
    ff_url = f"{api_base}/requests"
    return [
        (
            ff_url,
            build_purchase_body(
                customer_uid=customer_uid or fake.uuid4(),
                tier1_uid=tier1_uid,
                tier2_uid=tier2_uid,
                product_id=product_id,
                item_names=item_names,
                marketplace_id=marketplace_id,
                connection_id=connection_id,
            ),
        ) for _ in range(req_num)
    ]


def purchase(api_base, token, requests_number, **kwargs):
    product_id = kwargs['product_id']
    item_names = kwargs['items'].split(',')
    marketplace_id = kwargs['marketplace_id']

    post_tasks = build_post_tasks(api_base, product_id, item_names, marketplace_id, requests_number)
    asyncio.run(launch_requests(token, post_tasks))


def setup_commmand_parser(arg_subparsers):
    purchase_parser = arg_subparsers.add_parser('purchase', help='Creates purchase requests')
    purchase_parser.add_argument(
        "-p", "--product-id", dest='product_id', type=str,
        help='ID of a product for subscriptions, example: PRD-001-000-002',
    )
    # TODO: make it optional, extract items names from Product API if not passed
    purchase_parser.add_argument(
        "-i", "--items", type=str,
        help='list of items IDs, example: "PRD-001-000-002-0001","PRD-001-000-002-0002"',
    )
    # TODO: make it optional, extract marketplace from active Listings if not passed
    purchase_parser.add_argument(
        "-m", "--marketplace-id", dest='marketplace_id', type=str,
        help='ID of a marketplace where subscriptions are ordered, example: MP-55005'
    )
    purchase_parser.set_defaults(func=purchase)
