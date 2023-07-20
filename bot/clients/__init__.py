import math
import time
from typing import List, Union, Dict, Any

from bingX import ClientError
from bingX.perpetual.v1 import Perpetual as BingXClient

from ..utils.credentials import Credentials
from ejtraderCT import Ctrader as CtraderClient


class Client:
    def __init__(self, credentials: Credentials = None):
        self.name = credentials.name
        self.exchange_credentials = credentials.exchange_credentials
        self.broker_credentials = credentials.broker_credentials
        self.client = self._get_wrapped_client()

    def __repr__(self):
        return 'Client here'

    def _get_wrapped_client(self):
        if self.name == 'bingx':
            return _BingXClientWrapper(BingXClient(self.exchange_credentials.public_key,
                                                   self.exchange_credentials.private_key))
        return _CtraderClientWrapper(CtraderClient(self.broker_credentials.server,
                                            self.broker_credentials.account,
                                            self.broker_credentials.password),
                              self.name)


class _BingXClientWrapper:
    def __init__(self, client):
        self.client = client
        self.exception = ClientError

    def __repr__(self):
        return 'BingX Client Wrapper'

    def get_order_volume(self, symbol: str, quantity: float) -> float:
        response = self.client.latest_price(symbol)

        return quantity / float(response['tradePrice'])

    def change_margin_mode(self, symbol: str, margin_type: str) -> None:
        self.client.switch_margin_mode(symbol, margin_type)
        return

    def change_leverage(self, symbol: str, leverage: int) -> None:
        self.client.switch_leverage(symbol, 'Long', leverage)
        self.client.switch_leverage(symbol, 'Short', leverage)
        return

    def get_open_positions(self, symbol: str) -> List:
        return self.client.positions(symbol)

    def enter_position(self, symbol, side, action, entrust_volume, entrust_price, trade_type):
        return self.client.place_order(symbol=symbol,
                                       side=side,
                                       action=action,
                                       entrustPrice=entrust_price,
                                       entrustVolume=entrust_volume,
                                       tradeType=trade_type)

    def exit_position(self, symbol: str, position_id: str, quantity: float):
        return self.client.close_position(symbol, position_id)

    def error_handler(self, error, position_side, is_swap):
        if error.error_msg == 'position not exist':
            opposite_position = 'Long' if position_side == 'Short' else 'Short'
            position = position_side if not is_swap else opposite_position
            error_msg = f'NO {position.upper()} POSITION TO CLOSE'
        if error.error_code == 80012:
            error_msg = 'INSUFFICIENT FUNDS'
        return {'status': 'ERROR', 'error': error_msg.upper()}


class _CtraderClientWrapper:
    def __init__(self, client, name):
        self.client = client
        self.name = name
        self.exception = BaseException

    def __repr__(self):
        return f'{self.name.title()} Client Wrapper'

    def ping(self):
        checkConnection = self.client.isconnected()
        print("Is Connected?: ", checkConnection)

    # We calculate the number of lots for the give quantity
    def get_order_volume(self, symbol: str, quantity: float) -> float:
        lots = quantity / 100000
        return lots

    def change_margin_mode(self, symbol: str, margin_type: str) -> None:
        return

    def change_leverage(self, symbol: str, leverage: int) -> None:
        return

    def get_open_positions(self, symbol: str) -> object:
        # first for fetching the positions from the server
        time.sleep(0.1)
        positions = self.client.positions()
        time.sleep(0.1)
        if len(positions) > 0:
            open_positions = {'positions': [
                {
                    'positionId': positions[0]['pos_id'],
                    'positionSide': 'Long' if positions[0]['side'] == 'Buy' else 'Short',
                }
            ]
            }
        else:
            open_positions = {'positions': None}
        print('op')
        print(open_positions)
        return open_positions

    def enter_position(self, symbol, side, action, entrust_volume, entrust_price, trade_type):
        volume = entrust_volume if side == 'Bid' else -1 * entrust_volume
        if side == 'Bid':
            return self.client.buy(symbol=symbol, volume=entrust_volume, stoploss=0, takeprofit=0)
        else:
            return self.client.sell(symbol=symbol, volume=entrust_volume, stoploss=0, takeprofit=0)

    def exit_position(self, symbol: str, position_id: str, quantity: float):
        self.client.positionCloseById(position_id, quantity)

    def error_handler(self, error, position_side, is_swap):
        return {'status': 'ERROR', 'error': 'error'}

    def close_connection(self):
        self.client.logout()

# TODO convert this whole thing to async
# TODO refactor the cache and only use it for leverage and margin type... it makes closing trades very complicated