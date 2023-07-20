import json

from flask import request, g

from ..cache import Cache
from ..clients import Client
from ..services import BaseOrderService as OrderService
from ..trade import bp
from ..db import store_user_credentials


@bp.before_request
def find_user_credentials():
    store_user_credentials()


@bp.route('/trade/<exchange>', methods=['POST'])
def exchange_order(exchange):
    print(Cache.get_exchange(exchange))
    credentials = get_user_credentials(exchange)
    if credentials is None:
        return json.dumps({'status': 'NO_CREDENTIALS_FOUND'}), 400

    client = Client(credentials).client
    print(client)
    trade = json.loads(request.data)
    service = OrderService(client=client,
                           exchange=exchange,
                           symbol=trade['symbol'],
                           side=trade['side'],
                           action=trade['action'],
                           quantity=trade['quantity'],
                           trade_type=trade['trade_type'],
                           leverage=trade['leverage'] if 'leverage' in trade else 1,
                           safety=trade['safety'] if 'safety' in trade else False
                           )

    return service.start_order()


@bp.route('/trade/ctrader/<broker>', methods=['POST'])
async def broker_order(broker):
    # print(Cache.get_exchange(broker))
    credentials = get_user_credentials(broker)
    print(credentials)
    if credentials is None:
        return json.dumps({'status': 'NO_CREDENTIALS_FOUND'}), 400

    client = Client(credentials).client
    trade = json.loads(request.data)
    print(client)
    service = await OrderService(client=client,
                                 is_joint_symbol=True,
                                 exchange=broker,
                                 symbol=trade['symbol'],
                                 side=trade['side'],
                                 action=trade['action'],
                                 quantity=trade['quantity'],
                                 trade_type=trade['trade_type'],
                                 leverage=trade['leverage'] if 'leverage' in trade else 1,
                                 safety=trade['safety'] if 'safety' in trade else False
                                 )
    response = service.start_order()
    client.close_connection()
    return response


@bp.route('/trade/clear-cache', methods=['POST'])
def clear_cache():
    Cache.clear_cache()
    return json.dumps({'status': 'SUCCESS', 'msg': 'cache cleared'}), 200


def get_user_credentials(name: str):
    return next((credential for credential in g.user_credentials if credential.name == name), None)
