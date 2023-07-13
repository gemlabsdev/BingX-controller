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


class OrderService:
    open_orders = []

    def __init__(self,
                 client: Perpetual,
                 symbol: str = None,
                 side: str = None,
                 action: str = None,
                 quantity: float = 0,
                 trade_type: str = None,
                 margin: str = None,
                 leverage: int = 1):
        self.client = client
        self.symbol = _set_split_symbol(symbol)
        self.side = side
        self.action = action
        self.trade_type = trade_type
        self.entrust_price = 0
        self.leverage = leverage
        self.quantity = quantity * self.leverage
        self.entrust_volume = self._set_entrust_volume(self.quantity)
        self.margin = margin
        self.position_side = "Long" if self.side == 'Bid' else 'Short'
        self.exchange = 'BINGX'

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

    def get_open_position(self):
        response = self.client.positions(self.symbol)

        return response['positions'][0] if response['positions'] is not None else None

    def open_order(self):
        try:
            closed_order = self.close_order(is_only_close=False)
            if closed_order.get('status') == 'SAME_DIRECTION':
                return json.dumps({'status': 'REJECTED'})

            time_start = time.time()
            self.set_leverage()
            response = self.client.place_order(symbol=self.symbol,
                                               side=self.side,
                                               action=self.action,
                                               entrustPrice=self.entrust_price,
                                               entrustVolume=self.entrust_volume,
                                               tradeType=self.trade_type)
            logger.info(f'{self.exchange} - {self.symbol} - OPENED {self.position_side.upper()} POSITION - '
                        f'{stop_timer(time_start)}ms')

            return json.dumps(response)

        except ClientError as error:
            error_code = json.loads(error.error_msg)['Code']
            server_message = json.loads(error.error_msg)['Msg']
            error_msg = self._error_mapper(error_code, server_message)
            logger.error(f'{error_msg.upper()}')
            return {'ERROR': error_msg.upper()}

    def close_order(self, is_only_close=True):
        try:
            time_start = time.time()
            position = self.get_open_position()
            if position is None:
                if is_only_close:
                    logger.info(f'{self.exchange} - {self.symbol} - NO {self.position_side.upper()} POSITION TO CLOSE - '
                                f'{stop_timer(time_start)}ms')
                response = {'status': 'NOT_FOUND'}
                return json.dumps(response) if is_only_close else response

            position_side = position['positionSide']
            position_id = position['positionId']
            print(position_side)
            print(self.position_side)
            is_request_to_open_in_same_direction = position_side == self.position_side and self.action == 'Open'
            is_request_to_open_in_opposite_direction = position_side != self.position_side and self.action == 'Open'
            is_request_to_close_existing_position = position_side == self.position_side and self.action == 'Close'

            if is_request_to_open_in_same_direction:
                logger.warn(
                    f'{self.exchange} - {self.symbol} - {position_side.upper()} POSITION ALREADY IN PLACE - '
                    f'{stop_timer(time_start)}ms')
                return {'status': 'SAME_DIRECTION'}

            if is_request_to_open_in_opposite_direction or is_request_to_close_existing_position:
                response = self.client.close_position(symbol=self.symbol, positionId=position_id)
                logger.info(f'{self.exchange} - {self.symbol} - CLOSED {position_side.upper()} POSITION - '
                            f'{stop_timer(time_start)}ms')
                return json.dumps(response) if is_only_close else response

        except ClientError as error:
            if error.error_msg == 'position not exist':
                error_msg = 'position does not exist'
                logger.error(f'{error_msg.upper()}')

            else:
                error_code = json.loads(error.error_msg)['Code']
                server_message = json.loads(error.error_msg)['Msg']
                error_msg = self._error_mapper(error_code, server_message)
                logger.error(f'{error_msg.upper()}')

            return {'ERROR': error_msg.upper()}
