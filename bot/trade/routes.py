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
def perpetual_order(exchange):
    print(Cache.get_exchange(exchange))
    credentials = get_user_credentials(exchange)
    if credentials is None:
        return json.dumps({'status': 'NO_CREDENTIALS_FOUND'}), 400

    client = Client(credentials).client
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
    # case 'oanda':
    #     client = 3
    #
    # case _:
    #     return json.dumps({'status': 'NO_EXCHANGE_FOUND'}), 400


@bp.route('/trade/clear-cache', methods=['POST'])
def clear_cache():
    Cache.clear_cache()
    return json.dumps({'status': 'SUCCESS', 'msg': 'cache cleared'}), 200


def get_user_credentials(exchange: str):
    return next((credential for credential in g.user_credentials if credential.exchange == exchange), None)
