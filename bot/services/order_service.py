import json
import time
from typing import Union

from bingX import ClientError
from bingX.perpetual.v1 import Perpetual
from ..utils.logger import logger
from ..cache import Cache, Position


def _set_split_symbol(symbol: str, quote: str = 'USDT'):
    symbol_length = len(symbol)
    quote_length = len(quote)
    middle = symbol_length - quote_length

    return symbol[:middle] + "-" + symbol[middle:]


def stop_timer(time_start):
    return int((time.time() - time_start) * 1000)


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
                 margin: str = 'Isolated',
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

    def _set_entrust_volume(self, quantity: float):
        response = self.client.latest_price(self.symbol)
        asset_price = float(response['tradePrice'])

        return quantity / asset_price

    def set_margin_mode(self):
        margin = Cache.get_asset_margin(self.exchange, self.symbol)
        if self.margin != margin:
            self.client.switch_margin_mode(self.symbol, self.margin)
            Cache.set_asset_margin(self.exchange, self.symbol, self.margin)

    def set_leverage(self):
        leverage = Cache.get_asset_leverage(self.exchange, self.symbol)
        if self.leverage != leverage:
            self.client.switch_leverage(self.symbol, 'Long', self.leverage)
            self.client.switch_leverage(self.symbol, 'Short', self.leverage)
            Cache.set_asset_leverage(self.exchange, self.symbol, self.leverage)
            return

    def fetch_open_position(self) -> Position:
        position = Cache.get_asset_position(self.exchange, self.symbol)
        if position.get_id():
            return position
        response = self.client.positions(self.symbol)
        if api_positions := response['positions']:
            return Position(api_positions[0]['positionId'], api_positions[0]['positionSide'])

    def add_position_to_cache(self, position: Position) -> None:
        Cache.set_asset_position(self.exchange, self.symbol, position)

        return

    def remove_position_from_cache(self) -> None:
        Cache.remove_asset_position(self.exchange, self.symbol)

        return

    def log_message(self, message, timer, level='info'):
        if level == 'error':
            logger.error(f'{self.exchange.upper()} - {self.symbol} - {message} - {stop_timer(timer)}ms')
            return

        logger.info(f'{self.exchange.upper()} - {self.symbol} - {message} - {stop_timer(timer)}ms')

    def start_order(self):
        Cache.create_asset_cache(self.exchange, self.symbol)
        timer = time.time()
        try:
            position = self.fetch_open_position()
            if self.action == 'Close':
                if position is None:
                    self.log_message(f'NO {self.position_side.upper()} POSITION TO CLOSE', timer)
                    return json.dumps({'status': 'NOT_FOUND'})
                close_order = self.close_order(position.get_id())
                if close_order['status'] == 'ERROR':
                    return close_order
                self.log_message(f'CLOSED {self.position_side.upper()} POSITION', timer)
                return json.dumps({'status': 'SUCCESS'})

            if self.action == 'Open':
                if position is None:
                    self.open_order()
                    self.log_message(f'OPENED {self.position_side.upper()} POSITION', timer)
                    return json.dumps({'status': 'SUCCESS'})
                if position.get_side() == self.position_side:
                    self.log_message(f'{self.position_side.upper()} POSITION ALREADY IN PLACE', timer)
                    return {'status': 'SAME_DIRECTION'}
                if position.get_side() != self.position_side:
                    close_order = self.close_order(position.get_id())
                    if close_order['status'] == 'ERROR':
                        return close_order
                    self.log_message(f'CLOSED EXISTING {position.get_side().upper()} POSITION', timer)
                    open_order = self.open_order()
                    if open_order['status'] == 'ERROR':
                        return open_order
                    self.log_message(f'OPENED {self.position_side.upper()} POSITION', timer)
                    return json.dumps({'status': 'SUCCESS'})

        except ClientError as error:
            return self.handle_client_error(error, time.time())

    def open_order(self) -> object:
        try:
            self.set_leverage()
            self.set_margin_mode()
            response = self.client.place_order(symbol=self.symbol,
                                               side=self.side,
                                               action=self.action,
                                               entrustPrice=self.entrust_price,
                                               entrustVolume=self.entrust_volume,
                                               tradeType=self.trade_type)
            position = Position(response["orderId"], self.position_side)
            self.add_position_to_cache(position)
            return {"status": "SUCCESS"}

        except ClientError as error:

            return self.handle_client_error(error, time.time())

    def close_order(self, position_id: str) -> object:
        try:
            self.client.close_position(self.symbol, position_id)
            self.remove_position_from_cache()
            return {"status": "SUCCESS"}
        except ClientError as error:
            return self.handle_client_error(error, time.time())

    def handle_client_error(self, error, timer):
        if error.error_msg == 'position not exist':
            error_msg = 'position does not exist'
        else:
            error_code = json.loads(error.error_msg)['Code']
            server_message = json.loads(error.error_msg)['Msg']
            error_msg = self._error_mapper(error_code, server_message)
        self.log_message(f'{error_msg.upper()}', timer, 'error')

        return {'status': 'ERROR', 'error': error_msg.upper()}

    def _error_mapper(self, code, message):
        return self.error_msg_map[code] or message
