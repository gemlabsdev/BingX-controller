import json

from bingX.perpetual.v1 import Perpetual
from flask import request
from .. import PerpetualService
from ..trade import bp


def get_client():
    if 'client' not in g:
        g.client = Perpetual(Key.public_key, Key.private_key)

    return g.client


@bp.route('/perpetual/trade', methods=['POST'])
def perpetual_order():
    client = get_client()
    data = json.loads(request.data)
    service = PerpetualService(client=client,
                               symbol=data['symbol'],
                               side=data['side'],
                               action=data['action'],
                               quantity=data['quantity'],
                               trade_type=data['trade_type'],
                               leverage=data['leverage'] if 'leverage' in data else 1)
    if data['action'] == 'Open':
        return service.open_trade()
    if data['action'] == 'Close':
        return service.close_trade()