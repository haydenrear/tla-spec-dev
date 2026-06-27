from __future__ import annotations

from .types import ActionMetadata, StateGraphCase, StateGraphInput, StateGraphOutput


SCHEMA_VERSION = 'tla-testgraph.trace.v1'
SOURCE_MODULE = 'Internal'
SOURCE_VIEW = 'internal'
STATE_COUNT = 5
TRANSITION_COUNT = 4

CASES = [
    StateGraphCase(
        name='case_0001_create_account',
        before={'accounts': [], 'carts': {}, 'orders': {}, 'outbox': [], 'projections': {}},
        input=StateGraphInput(
            action='CreateAccount',
            source_node='1588591107832274314',
            target_node='-5087608892121480267',
            params={'account': 'acct-1'},
        ),
        output={'body': {'account': 'acct-1'}, 'status': 201},
        after={'accounts': ['acct-1'], 'carts': {}, 'orders': {}, 'outbox': [], 'projections': {}},
        labels=frozenset(('CreateAccount',)),
        schema_version=SCHEMA_VERSION,
        view=SOURCE_VIEW,
        layer='internal',
        controllability='unit_direct',
        generates=frozenset(('spec_unit',)),
        tags=frozenset(()),
        metadata=ActionMetadata(
            layer='internal',
            controllability='unit_direct',
            generates=frozenset(('spec_unit',)),
            tags=frozenset(()),
        ),
    ),
    StateGraphCase(
        name='case_0002_add_cart_item',
        before={'accounts': ['acct-1'], 'carts': {}, 'orders': {}, 'outbox': [], 'projections': {}},
        input=StateGraphInput(
            action='AddCartItem',
            source_node='-5087608892121480267',
            target_node='-2678954437951011996',
            params={'account': 'acct-1', 'sku': 'sku-1'},
        ),
        output={'body': {'account': 'acct-1', 'sku': 'sku-1'}, 'status': 202},
        after={'accounts': ['acct-1'], 'carts': {'acct-1': ['sku-1']}, 'orders': {}, 'outbox': [], 'projections': {}},
        labels=frozenset(('AddCartItem',)),
        schema_version=SCHEMA_VERSION,
        view=SOURCE_VIEW,
        layer='internal',
        controllability='unit_direct',
        generates=frozenset(('spec_unit',)),
        tags=frozenset(()),
        metadata=ActionMetadata(
            layer='internal',
            controllability='unit_direct',
            generates=frozenset(('spec_unit',)),
            tags=frozenset(()),
        ),
    ),
    StateGraphCase(
        name='case_0003_checkout',
        before={'accounts': ['acct-1'], 'carts': {'acct-1': ['sku-1']}, 'orders': {}, 'outbox': [], 'projections': {}},
        input=StateGraphInput(
            action='Checkout',
            source_node='-2678954437951011996',
            target_node='-197687801133262627',
            params={'account': 'acct-1', 'order': 'order-1'},
        ),
        output={'body': {'order': 'order-1', 'status': 'accepted'}, 'status': 202},
        after={'accounts': ['acct-1'], 'carts': {'acct-1': ['sku-1']}, 'orders': {'order-1': {'account': 'acct-1', 'items': ['sku-1'], 'status': 'accepted'}}, 'outbox': [{'order_id': 'order-1', 'event': 'OrderAccepted'}], 'projections': {}},
        labels=frozenset(('Checkout',)),
        schema_version=SCHEMA_VERSION,
        view=SOURCE_VIEW,
        layer='internal',
        controllability='unit_direct',
        generates=frozenset(('spec_unit',)),
        tags=frozenset(()),
        metadata=ActionMetadata(
            layer='internal',
            controllability='unit_direct',
            generates=frozenset(('spec_unit',)),
            tags=frozenset(()),
        ),
    ),
    StateGraphCase(
        name='case_0004_project_order',
        before={'accounts': ['acct-1'], 'carts': {'acct-1': ['sku-1']}, 'orders': {'order-1': {'account': 'acct-1', 'items': ['sku-1'], 'status': 'accepted'}}, 'outbox': [{'order_id': 'order-1', 'event': 'OrderAccepted'}], 'projections': {}},
        input=StateGraphInput(
            action='ProjectOrder',
            source_node='-197687801133262627',
            target_node='-1908824217334352009',
            params={'order': 'order-1'},
        ),
        output={'body': {'processed': 1}, 'status': 200},
        after={'accounts': ['acct-1'], 'carts': {'acct-1': ['sku-1']}, 'orders': {'order-1': {'account': 'acct-1', 'items': ['sku-1'], 'status': 'accepted'}}, 'outbox': [], 'projections': {'order-1': 'ready_to_ship'}},
        labels=frozenset(('ProjectOrder',)),
        schema_version=SCHEMA_VERSION,
        view=SOURCE_VIEW,
        layer='internal',
        controllability='unit_direct',
        generates=frozenset(('spec_unit',)),
        tags=frozenset(()),
        metadata=ActionMetadata(
            layer='internal',
            controllability='unit_direct',
            generates=frozenset(('spec_unit',)),
            tags=frozenset(()),
        ),
    ),
]

CASES_BY_NAME = {case.name: case for case in CASES}
