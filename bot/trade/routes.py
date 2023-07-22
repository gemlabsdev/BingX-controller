import json
import re
from flask import request, g

from ..cache import Cache
from ..clients import Client
from ..services import BaseOrderService as OrderService
from ..trade import bp
from ..db import store_user_credentials


def _sanitize_symbol(symbol: str, intermediary: str):
    _symbol = re.sub(r"\..*", '', symbol)
    if intermediary == 'exchange':
        return _set_split_symbol(_symbol)
    else:
        return _symbol


def _set_split_symbol(symbol: str, quote: str = 'USDT'):
    symbol_length = len(symbol)
    quote_length = len(quote)
    middle = symbol_length - quote_length

    return symbol[:middle] + "-" + symbol[middle:]


@bp.before_request
def find_user_credentials():
    store_user_credentials()


@bp.route('/trade/<intermediary>/<agent>', methods=['POST'])
def exchange_order(intermediary, agent):
    credentials = get_user_credentials(agent)
    print(credentials)
    if credentials is None:
        return json.dumps({'status': 'NO_CREDENTIALS_FOUND'}), 400

    client = Client(credentials=credentials, intermediary=intermediary).client
    client.ping()
    trade = json.loads(request.data)
    sanitized_symbol = _sanitize_symbol(trade['symbol'], intermediary)
    service = OrderService(client=client,
                           agent=agent,
                           symbol=sanitized_symbol,
                           side=trade['side'],
                           action=trade['action'],
                           quantity=trade['quantity'],
                           trade_type=trade['trade_type'],
                           leverage=trade['leverage'] if 'leverage' in trade else 1,
                           safety=trade['safety'] if 'safety' in trade else False
                           )

    response = service.start_order()
    if intermediary == 'broker':
        client.close_connection()
    return response


@bp.route('/trade/clear-cache', methods=['POST'])
def clear_cache():
    Cache.clear_cache()
    return json.dumps({'status': 'SUCCESS', 'msg': 'cache cleared'}), 200


def get_user_credentials(name: str):
    return next((credential for credential in g.user_credentials if credential.name == name), None)
