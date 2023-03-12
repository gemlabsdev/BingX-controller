import json
import time

from bingX.perpetual.v1 import Perpetual
from logger import logger
from Cache import Cache


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
        self.symbol = self._set_split_symbol(symbol)
        self.side = side
        self.action = action
        self.trade_type = trade_type
        self.entrust_price = 0
        self.entrust_volume = self._set_entrust_volume(quantity)
        self.margin = margin
        self.leverage = leverage
        self.position_side = "Long" if self.side == 'Bid' else 'Short'

    def _set_split_symbol(self, symbol: str, quote: str = 'USDT'):
        symbol_length = len(symbol)
        quote_length = len(quote)
        middle = symbol_length - quote_length

        return symbol[:middle] + "-" + symbol[middle:]

    def _set_entrust_volume(self, quantity: float):
        response = self.client.latest_price(self.symbol)
        asset_price = float(response['tradePrice'])

        return quantity / asset_price

    def set_margin_mode(self):
        self.client.switch_margin_mode(self.symbol, self.margin)

    def set_leverage(self):
        self.client.switch_leverage(self.symbol, 'Long', self.leverage)
        self.client.switch_leverage(self.symbol, 'Short', self.leverage)
        logger.info(f'Leverage for {self.symbol} successfully set to {self.leverage}x')

    def get_open_position(self):
        cached_position = Cache.open_positions.get(self.symbol)
        if cached_position is None:
            logger.info(f'No cached positions for {self.symbol}')
            logger.info(f'Requesting open {self.symbol} positions from BingX')
            response = self.client.positions(self.symbol)
            logger.info(f'Adding {self.symbol} {self.position_side} position to cache')
            if response['positions'] is None:
                return
            position_id = response['positions'][0]['positionId']
            position_side = response['positions'][0]['positionSide']
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

    def remove_position_from_cache(self):
        cached_position_side = Cache.open_positions[self.symbol]['positionSide']
        logger.info(f'Removing {self.symbol} {cached_position_side} position from cache')
        Cache.open_positions[self.symbol] = {'positionId': None,
                                             'positionSide': None}
        return

    def open_trade(self):
        start_time_open_close = time.time()
        closed_trade = self.close_trade(is_only_close=False)
        if closed_trade.get('status') == 'SAME_DIRECTION':
            logger.warn(f'REJECTED: A {self.position_side} position for {self.symbol} is already in place. '
                        f'Close position to place a new one')
            logger.info(f'-----------------REQUEST-FINISHED-----------------------')
            response = json.dumps({'status': 'REJECTED'})
            return response
        start_time_open = time.time()
        logger.info(f'---------------------OPEN-POSITION----------------------')
        logger.info(f'Opening new {self.position_side} for {self.symbol}')
        response = self.client.place_order(symbol=self.symbol,
                                           side=self.side,
                                           action=self.action,
                                           entrustPrice=self.entrust_price,
                                           entrustVolume=self.entrust_volume,
                                           tradeType=self.trade_type)
        logger.info(f'OPEN-POSITION: DONE IN {int((time.time() - start_time_open)*1000)}ms')
        logger.info(f'--------------------TOTAL-ORDER-TIME--------------------')
        logger.info(f'CLOSE-OPEN-REQUEST DONE IN {int((time.time() - start_time_open_close)*1000)}ms')
        logger.info(f'---------------------CACHE-POSITION---------------------')
        start_time_cache = time.time()
        position = self.get_api_open_position()
        print(position)
        self.add_position_to_cache(position['positionId'], position['positionSide'])
        logger.info(f'CACHE-POSITION: DONE IN {int((time.time() - start_time_cache)*1000)}ms')
        logger.info(f'-----------------REQUEST-FINISHED-----------------------')
        return response

    def close_trade(self, is_only_close=True):
        start_time_close = time.time()
        if is_only_close:
            logger.info(f'---------------------CLOSE-POSITION---------------------')
        else:
            logger.info(f'-----------------CLOSE-EXISTING-POSITION----------------')
        position = self.get_open_position()
        if position is None or not any(Cache.open_positions):
            logger.info(f'No open positions for {self.symbol}')
            logger.info(f'CLOSE-POSITION: DONE IN {int((time.time() - start_time_close)*1000)}ms')
            logger.info(f'-----------------REQUEST-FINISHED-----------------------')
            response = {'status': 'NOTHING_TO_CLOSE'}
            return json.dumps(response) if is_only_close else response
        position_side = position['positionSide']
        position_id = position['positionId']
        if position_side == self.position_side and self.action == 'Open':
            return {'status': 'SAME_DIRECTION'}
        if not is_only_close:
            logger.warn(f'Open position found - Only 1 open position per symbol allowed')
        logger.info(f'Closing {position_side.upper()} position for {self.symbol}')
        response = self.client.close_position(symbol=self.symbol, positionId=position_id)
        print(response)
        logger.info(f'CLOSE-POSITION: DONE IN {int((time.time() - start_time_close) * 1000)}ms')
        self.remove_position_from_cache()
        logger.info(f'----------------REQUEST-FINISHED----------------------')

        return response

