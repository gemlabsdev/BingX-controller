import json
import time

from bingX import ClientError
from bingX.perpetual.v1 import Perpetual
from ..utils.logger import logger
from ..utils.cache import Cache


def _set_split_symbol(symbol: str, quote: str = 'USDT'):
    symbol_length = len(symbol)
    quote_length = len(quote)
    middle = symbol_length - quote_length

    return symbol[:middle] + "-" + symbol[middle:]


def stop_timer(time_start):
    return int((time.time() - time_start) * 1000)


def get_open_position():
    return OrderService.open_position


def set_open_position(position):
    OrderService.open_position = position
    return get_open_position()


def get_open_position_id():
    return None if OrderService.open_position is None else OrderService.open_position['positionId']


def get_open_position_side():
    return None if OrderService.open_position is None else OrderService.open_position['positionSide']


class OrderService:
    open_position = None

    def __init__(self,
                 client: Perpetual,
                 symbol: str = None,
                 exchange: str = None,
                 side: str = None,
                 action: str = None,
                 quantity: float = 0,
                 trade_type: str = None,
                 margin: str = None,
                 leverage: int = 1):
        self.client = client
        self.symbol = _set_split_symbol(symbol)
        self.exchange = exchange
        self.side = side
        self.action = action
        self.trade_type = trade_type
        self.entrust_price = 0
        self.leverage = leverage
        self.quantity = quantity * self.leverage
        self.entrust_volume = self._set_entrust_volume(self.quantity)
        self.margin = margin
        self.position_side = "Long" if self.side == 'Bid' else 'Short'

        self.error_msg_map = {
            100001: 'Signature authentication failed',
            100202: 'Insufficient balance',
            101204: 'Insufficient balance',
            101400: 'Insuficient volume',
            100400: 'Invalid parameter',
            100440: 'Order price deviates greatly from the market price',
            100500: 'Internal server error',
            100503: 'Server busy',
        }

    def _error_mapper(self, code, message):
        return self.error_msg_map[code] or message

    def _set_entrust_volume(self, quantity: float):
        response = self.client.latest_price(self.symbol)
        asset_price = float(response['tradePrice'])

        return quantity / asset_price

    def set_margin_mode(self):
        self.client.switch_margin_mode(self.symbol, self.margin)

    def set_leverage(self):
        self.client.switch_leverage(self.symbol, 'Long', self.leverage)
        self.client.switch_leverage(self.symbol, 'Short', self.leverage)

    def fetch_open_position(self):
        response = self.client.positions(self.symbol)
        return set_open_position(response['positions'][0] if response['positions'] is not None else None)

    def add_position_to_cache(self, position_id=None, position_side=None):
        Cache.open_positions[self.symbol] = {'positionId': position_id,
                                             'positionSide': position_side}
        return

    def add_leverage_to_cache(self, leverage):
        Cache.symbol_leverage[self.symbol] = leverage
        return

    def remove_position_from_cache(self):
        Cache.open_positions[self.symbol] = {'positionId': None,
                                             'positionSide': None}
        return

    def log_message(self, message, timer, level='info'):
        if level == 'error':
            logger.error(f'{self.exchange.upper()} - {self.symbol} - {message} - {stop_timer(timer)}ms')
            return

        logger.info(f'{self.exchange.upper()} - {self.symbol} - {message} - {stop_timer(timer)}ms')

    def start_order(self):
        print(self.exchange)
        timer = time.time()
        try:
            position = self.fetch_open_position()
            if self.action == 'Close':
                if position is None:
                    self.log_message(f'NO {self.position_side.upper()} POSITION TO CLOSE', timer)
                    return json.dumps({'status': 'NOT_FOUND'})
                self.close_order()
                self.log_message(f'CLOSED {self.position_side.upper()} POSITION', timer)
                return json.dumps({'status': 'SUCCESS'})

            if self.action == 'Open':
                if position is None:
                    self.open_order()
                    self.log_message(f'OPENED {self.position_side.upper()} POSITION', timer)
                    return json.dumps({'status': 'SUCCESS'})
                if position['positionSide'] == self.position_side:
                    self.log_message(f'{self.position_side.upper()} POSITION ALREADY IN PLACE', timer)
                    return {'status': 'SAME_DIRECTION'}
                if position['positionSide'] != self.position_side:
                    self.close_order()
                    self.log_message(f'CLOSED EXISTING {get_open_position_side().upper()} POSITION', timer)
                    self.open_order()
                    self.log_message(f'OPENED {self.position_side.upper()} POSITION', timer)
                    return json.dumps({'status': 'SUCCESS'})

        except ClientError as error:
            if error.error_msg == 'position not exist':
                error_msg = 'position does not exist'
            else:
                error_code = json.loads(error.error_msg)['Code']
                server_message = json.loads(error.error_msg)['Msg']
                error_msg = self._error_mapper(error_code, server_message)
            self.log_message(f'{error_msg.upper()}', timer, 'error')

            return {'ERROR': error_msg.upper()}

    def open_order(self):
        self.set_leverage()
        response = self.client.place_order(symbol=self.symbol,
                                           side=self.side,
                                           action=self.action,
                                           entrustPrice=self.entrust_price,
                                           entrustVolume=self.entrust_volume,
                                           tradeType=self.trade_type)

        return response

    def close_order(self):
        positionId = get_open_position_id()
        print(positionId)
        response = self.client.close_position(self.symbol, positionId)

        return response
