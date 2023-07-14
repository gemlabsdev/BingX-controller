import json

from bingX.perpetual.v1 import Perpetual
from flask import request, g

from ..cache import Cache
from ..services.order_service import OrderService
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
    client = Perpetual(credentials.public_key, credentials.private_key)
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


@bp.route('/trade/clear-cache', methods=['POST'])
def clear_cache():
    Cache.clear_cache()
    return json.dumps({'status': 'SUCCESS', 'msg': 'cache cleared'}), 200


def get_user_credentials(exchange):
    return next((credential for credential in g.user_credentials if credential.exchange == exchange), None)
