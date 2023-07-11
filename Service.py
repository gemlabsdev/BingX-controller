import json
import time

from bingX import ClientError
from bingX.perpetual.v1 import Perpetual
from logger import logger
from Cache import Cache


def _set_split_symbol(symbol: str, quote: str = 'USDT'):
    symbol_length = len(symbol)
    quote_length = len(quote)
    middle = symbol_length - quote_length

    return symbol[:middle] + "-" + symbol[middle:]


class PerpetualService:
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
        cached_leverage = Cache.symbol_leverage.get(self.symbol)
        if cached_leverage is None or cached_leverage != self.leverage:
            logger.info(f'SETTING TRADE LEVERAGE')
            self.client.switch_leverage(self.symbol, 'Long', self.leverage)
            self.client.switch_leverage(self.symbol, 'Short', self.leverage)
            logger.info(f'Leverage for {self.symbol} successfully set to {self.leverage}x')
            self.add_leverage_to_cache(self.symbol, self.leverage)
        else:
            return

    def get_open_position(self):
        cached_position = Cache.open_positions.get(self.symbol)
        if cached_position is None:
            logger.info(f'No cached positions for {self.symbol}')
            logger.info(f'Requesting open {self.symbol} positions from BingX')
            response = self.client.positions(self.symbol)
            if response['positions'] is None:
                return
            position_id = response['positions'][0]['positionId']
            position_side = response['positions'][0]['positionSide']
            logger.info(f'Adding {self.symbol} {self.position_side} position to cache')
            self.add_position_to_cache(position_id, position_side)
            return response['positions'][0]
        logger.info(f'Finding open {self.symbol} positions in cache')
        if cached_position['positionId'] is None:
            return
        return cached_position

    def get_api_open_position(self):
        logger.info(f'Requesting open {self.symbol} positions from BingX for caching')
        response = self.client.positions(self.symbol)
        if response['positions'] is None:
            return
        return response['positions'][0]

    def add_position_to_cache(self, position_id=None, position_side=None):
        logger.info(f'Adding {self.symbol} {self.position_side} position to cache')
        Cache.open_positions[self.symbol] = {'positionId': position_id,
                                             'positionSide': position_side}
        return

    def add_leverage_to_cache(self, symbol, leverage):
        logger.info(f'Saving {symbol} leverage of {leverage}X to cache')
        Cache.symbol_leverage[symbol] = leverage
        return

    def remove_position_from_cache(self):
        cached_position_side = Cache.open_positions[self.symbol]['positionSide']
        logger.info(f'Removing {self.symbol} {cached_position_side} position from cache')
        Cache.open_positions[self.symbol] = {'positionId': None,
                                             'positionSide': None}
        return

    def open_trade(self):
        try:
            start_time_open_close = time.time()
            closed_trade = self.close_trade(is_only_close=False)
            if closed_trade.get('status') == 'SAME_DIRECTION':
                logger.warn(f'A {self.position_side} position for {self.symbol} is already in place. '
                            f'Close position to place a new one')
                logger.info(f'-----------------REQUEST-FINISHED-----------------------')
                response = json.dumps({'status': 'REJECTED'})
                return response
            if closed_trade.get('status') == 'NO_POSITION_FOUND':
                logger.warn(f' Nothing to close')
                logger.info(f'-----------------REQUEST-FINISHED-----------------------')
                response = json.dumps({'status': 'REJECTED'})
                return response
            start_time_open = time.time()
            logger.info(f'---------------------OPEN-POSITION----------------------')
            self.set_leverage()
            logger.info(f'Opening new {self.position_side} for {self.symbol}')
            response = self.client.place_order(symbol=self.symbol,
                                               side=self.side,
                                               action=self.action,
                                               entrustPrice=self.entrust_price,
                                               entrustVolume=self.entrust_volume,
                                               tradeType=self.trade_type)
            logger.info(f'OPEN-POSITION: DONE IN {int((time.time() - start_time_open) * 1000)}ms')
            logger.info(f'--------------------TOTAL-ORDER-TIME--------------------')
            logger.info(f'CLOSE-OPEN-REQUEST DONE IN {int((time.time() - start_time_open_close) * 1000)}ms')
            logger.info(f'---------------------CACHE-POSITION---------------------')
            start_time_cache = time.time()
            position = self.get_api_open_position()
            self.add_position_to_cache(position['positionId'], position['positionSide'])
            logger.info(f'CACHE-POSITION: DONE IN {int((time.time() - start_time_cache) * 1000)}ms')
            logger.info(f'-----------------REQUEST-FINISHED-----------------------')
            print(Cache.symbol_leverage)
            return response

        except ClientError as error:
            error_code = json.loads(error.error_msg)['Code']
            server_message = json.loads(error.error_msg)['Msg']
            error_msg = self._error_mapper(error_code, server_message)
            logger.error(f'{error_msg.upper()}')
            return {'ERROR': error_msg.upper()}

    def close_trade(self, is_only_close=True):
        try:
            start_time_close = time.time()
            if is_only_close:
                logger.info(f'---------------------CLOSE-POSITION---------------------')
            else:
                logger.info(f'-----------------CLOSE-EXISTING-POSITION----------------')
            position = self.get_open_position()
            if position is None or not any(Cache.open_positions):
                logger.info(f'No cached open positions for {self.symbol}')
                logger.info(f'CLOSE-POSITION: DONE IN {int((time.time() - start_time_close) * 1000)}ms')
                logger.info(f'-----------------REQUEST-FINISHED-----------------------')
                response = {'status': 'NOTHING_TO_CLOSE'}
                return json.dumps(response) if is_only_close else response
            position_side = position['positionSide']
            position_id = position['positionId']
            if position_side == self.position_side and self.action == 'Open':
                return {'status': 'SAME_DIRECTION'}
            if not is_only_close:
                logger.warn(f'Open position found - Only 1 open position per symbol allowed')
            if (position_side == self.position_side and self.action == 'Close') \
                    or (position_side != self.position_side and self.action == 'Open'):
                logger.info(f'Closing {position_side.upper()} position for {self.symbol}')
                response = self.client.close_position(symbol=self.symbol, positionId=position_id)
                logger.info(f'CLOSE-POSITION: DONE IN {int((time.time() - start_time_close) * 1000)}ms')
                self.remove_position_from_cache()
                logger.info(f'----------------REQUEST-FINISHED----------------------')
                return response
            else:
                logger.warn(f'No position found')
                return {'status': 'NO_POSITION_FOUND'}

        except ClientError as error:
            if error.error_msg == 'position not exist':
                error_msg = 'position does not exist'
                logger.error(f'{error_msg.upper()}')
                self.remove_position_from_cache()

            else:
                error_code = json.loads(error.error_msg)['Code']
                server_message = json.loads(error.error_msg)['Msg']
                error_msg = self._error_mapper(error_code, server_message)
                logger.error(f'{error_msg.upper()}')

            return {'ERROR': error_msg.upper()}
