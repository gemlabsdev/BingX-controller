import math
import time
import ccxt
from typing import List, Union, Dict, Any
from bingX import ClientError
from bingX.perpetual.v1 import Perpetual as BingXClient
from ..utils.credentials import Credentials
from ejtraderCT import Ctrader as CtraderClient


def _generate_broker_position_object(positions: List):
    if len(positions) > 0:
        open_positions = {'positions': [
            {
                'positionId': positions[0]['pos_id'],
                'positionSide': 'LONG' if positions[0]['side'] == 'Buy' else 'SHORT',
            }
        ]
        }
    else:
        open_positions = {'positions': None}
    return open_positions


def _generate_exchange_position_object(positions: List):
    if len(positions) > 0:
        open_positions = {'positions': [
            {
                'positionId': positions[0]['info']['positionId'],
                'positionSide': positions[0]['info']['positionSide'].upper(),
            }
        ]
        }
    else:
        open_positions = {'positions': None}
    return open_positions


class Client:
    def __init__(self, credentials: Credentials, intermediary: str):
        self.name = credentials.name
        self.intermediary = intermediary
        self.exchange_credentials = credentials.exchange_credentials
        self.broker_credentials = credentials.broker_credentials
        self.client = self._get_wrapped_client()

    def __repr__(self):
        return 'Client here'

    def _get_exchange_client(self):
        exchange_class = getattr(ccxt, self.name)
        return exchange_class({
            'apiKey': self.exchange_credentials.public_key,
            'secret': self.exchange_credentials.private_key,
            'rateLimit': 10,
            # must be specific to exchange
            'options': {
                'defaultType': 'swap',
            }
        })

    def _get_broker_client(self):
        return CtraderClient(self.broker_credentials.server,
                             self.broker_credentials.account,
                             self.broker_credentials.password)

    def _get_wrapped_client(self):
        if self.intermediary == 'exchange':
            return _ExchangeClientWrapper(self._get_exchange_client())
        else:
            return _CtraderClientWrapper(self._get_broker_client())


class _ExchangeClientWrapper:
    def __init__(self, client):
        self.client = client
        self.exception = BaseException

    def __repr__(self):
        return f'{self.client.name.title()} Client Wrapper'

    def get_order_amount(self, symbol: str, quantity: float) -> float:

        response = self.client.fetch_ticker(symbol)
        return quantity / float(response['last'])

    def change_margin_mode(self, symbol: str, margin_type: str) -> None:
        self.client.setMarginMode(margin_type, symbol)
        return

    def change_leverage(self, symbol: str, leverage: int) -> None:
        self.client.set_leverage(leverage, symbol, {'side': 'LONG'})
        self.client.set_leverage(leverage, symbol, {'side': 'SHORT'})
        return

    def get_open_positions(self, symbol: str):
        positions = self.client.fetch_positions([symbol])
        return _generate_exchange_position_object(positions)

    def enter_position(self, symbol, trade_type, side, amount, position_side):
        params = {'positionSide': position_side}
        return self.client.create_order(symbol=symbol,
                                        type=trade_type,
                                        side=side,
                                        amount=amount,
                                        params=params)

    def exit_position(self, symbol: str, trade_type: str, side: str, amount: float, position_id: str, quantity: float):
        positions = self.client.fetch_positions([symbol])
        position_amount = float(positions[0]['info']['positionAmt'])
        position_side = positions[0]['info']['positionSide']
        params = {'reduce_only': True, 'positionSide': position_side}
        return self.client.create_order(symbol=symbol,
                                        type=trade_type,
                                        side='buy' if position_side == 'SHORT' else 'sell',
                                        amount=position_amount,
                                        params=params)

    def error_handler(self, error, position_side, is_swap):
        if error.error_msg == 'position not exist':
            opposite_position = 'Long' if position_side == 'Short' else 'Short'
            position = position_side if not is_swap else opposite_position
            error_msg = f'NO {position.upper()} POSITION TO CLOSE'
        if error.error_code == 80012:
            error_msg = 'INSUFFICIENT FUNDS'
        return {'status': 'ERROR', 'error': error_msg.upper()}


class _CtraderClientWrapper:
    def __init__(self, client):
        self.client = client
        self.exception = BaseException

    def __repr__(self):
        return f'{self.client.name.title()} Client Wrapper'

    # We calculate the number of lots for the give quantity
    def get_order_amount(self, symbol: str, quantity: float) -> float:
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

        return _generate_broker_position_object(positions)

    def enter_position(self, symbol, trade_type, side, amount, position_side):
        volume = amount if side == 'buy' else -1 * amount
        if side == 'buy':
            return self.client.buy(symbol=symbol, volume=amount, stoploss=0, takeprofit=0)
        else:
            return self.client.sell(symbol=symbol, volume=amount, stoploss=0, takeprofit=0)

    def exit_position(self, symbol: str, trade_type: str, side: str, amount: float, position_id: str, quantity: float):
        self.client.positionCloseById(position_id, quantity)

    def error_handler(self, error, position_side, is_swap):
        return {'status': 'ERROR', 'error': 'error'}

    def close_connection(self):
        self.client.logout()

# TODO convert this whole thing to async
# TODO refactor the cache and only use it for leverage and margin type... it makes closing trades very complicated
