import json

from bingX.perpetual.v1 import Perpetual
from flask import request, g
from ..services.order_service import OrderService
from ..trade import bp
from ..db import store_user_credentials


@bp.before_request
def find_user_credentials():
    store_user_credentials()


@bp.route('/trade/<exchange>', methods=['POST'])
def perpetual_order(exchange):
    credentials = get_user_credentials(exchange)
    print(credentials)
    if credentials is None:
        return {'status': 'NO_POSITION_FOUND'}, 400
    client = Perpetual(credentials.public_key, credentials.private_key)
    trade = json.loads(request.data)
    service = OrderService(client=client,
                           symbol=trade['symbol'],
                           side=trade['side'],
                           action=trade['action'],
                           quantity=trade['quantity'],
                           trade_type=trade['trade_type'],
                           leverage=trade['leverage'] if 'leverage' in trade else 1)
    if trade['action'] == 'Open':
        return service.open_order()
    if trade['action'] == 'Close':
        return service.close_order()


def get_user_credentials(exchange):
    return next((credential for credential in g.user_credentials if credential.exchange == exchange), None)
