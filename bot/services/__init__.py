import json
import time

from ..utils.logger import logger
from ..cache import Cache, Position


def _set_split_symbol(symbol: str, quote: str = 'USDT'):
    symbol_length = len(symbol)
    quote_length = len(quote)
    middle = symbol_length - quote_length

    return symbol[:middle] + "-" + symbol[middle:]


def stop_timer(time_start):
    return int((time.time() - time_start) * 1000)


class BaseOrderService:
    open_position = None

    def __init__(self,
                 client: any = None,
                 symbol: str = None,
                 is_joint_symbol: bool = False,
                 exchange: str = None,
                 side: str = None,
                 action: str = None,
                 quantity: float = 0,
                 trade_type: str = None,
                 margin: str = 'Isolated',
                 leverage: int = 1,
                 safety: bool = False
                 ):
        self.client = client
        self.symbol = _set_split_symbol(symbol) if not is_joint_symbol else symbol
        self.exchange = exchange
        self.side = side
        self.action = action
        self.trade_type = trade_type
        self.entrust_price = 0
        self.leverage = leverage
        self.quantity = quantity * self.leverage
        self.entrust_volume = self._set_entrust_volume()
        self.margin = margin
        self.position_side = "Long" if self.side == 'Bid' else 'Short'
        self.safety = safety
        self.is_swap = False

    def _set_entrust_volume(self):
        return self.client.get_order_volume(self.symbol, self.quantity)

    def set_margin_mode(self):
        margin = Cache.get_asset_margin(self.exchange, self.symbol)
        if self.margin != margin:
            # client mapper margin mode
            self.client.change_margin_mode(self.symbol, self.margin)
            Cache.set_asset_margin(self.exchange, self.symbol, self.margin)

    def set_leverage(self):
        leverage = Cache.get_asset_leverage(self.exchange, self.symbol)
        if self.leverage != leverage:
            self.client.change_leverage(self.symbol, self.leverage)
            Cache.set_asset_leverage(self.exchange, self.symbol, self.leverage)
            return

    def fetch_open_position(self, force=False) -> Position:
        position = Cache.get_asset_position(self.exchange, self.symbol)
        if position.get_id() is not None and not force:
            return position
        response = self.client.get_open_positions(self.symbol)
        if api_positions := response['positions']:
            print(api_positions[0]['positionId'])
            return Position(api_positions[0]['positionId'], api_positions[0]['positionSide'])

    def update_cache(self) -> None:
        position = self.fetch_open_position(force=True)
        if position is None:
            Cache.remove_asset_position(self.exchange, self.symbol)
            return
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
        position = self.fetch_open_position()
        if self.action == 'Close':
            safety_message = 'SAFETY HOOK - ' if self.safety else ''
            if position is None or position.get_side() != self.position_side:
                self.log_message(f'{safety_message}NO {self.position_side.upper()} POSITION TO CLOSE', timer)
                return json.dumps({'status': 'NOT_FOUND'})
            close_order = self.close_order(position.get_id())
            if close_order['status'] == 'ERROR':
                self.update_cache()
                return close_order
            self.log_message(f'{safety_message}CLOSED {self.position_side.upper()} POSITION', timer)
            return json.dumps({'status': 'SUCCESS'})

        if self.action == 'Open':
            if position is None:
                open_order = self.open_order()
                if open_order['status'] == 'ERROR':
                    self.update_cache()
                    return open_order
                self.log_message(f'OPENED {self.position_side.upper()} POSITION', timer)
                return json.dumps({'status': 'SUCCESS'})
            if position.get_side() == self.position_side:
                self.log_message(f'{self.position_side.upper()} POSITION ALREADY IN PLACE', timer)
                return {'status': 'SAME_DIRECTION'}
            if position.get_side() != self.position_side:
                self.is_swap = True
                close_order = self.close_order(position.get_id())
                if close_order['status'] == 'ERROR':
                    self.update_cache()
                    return close_order
                opposite_position = 'Long' if self.position_side == 'Short' else 'Short'
                self.log_message(f'CLOSED EXISTING {opposite_position.upper()} POSITION', timer)
                open_order = self.open_order()
                if open_order['status'] == 'ERROR':
                    self.update_cache()
                    return open_order
                self.log_message(f'OPENED {self.position_side.upper()} POSITION', timer)
                return json.dumps({'status': 'SUCCESS'})

    def open_order(self):
        try:
            self.set_leverage()
            self.set_margin_mode()
            response = self.client.enter_position(symbol=self.symbol,
                                                  side=self.side,
                                                  action=self.action,
                                                  entrust_price=self.entrust_price,
                                                  entrust_volume=self.entrust_volume,
                                                  trade_type=self.trade_type)
            time.sleep(0.2)
            self.update_cache()
            return {"status": "SUCCESS"}

        except self.client.exception as error:
            return self.handle_client_error(error, time.time())

    def close_order(self, position_id: str) -> object:
        try:
            time.sleep(1)
            self.client.exit_position(self.symbol, position_id, self.quantity)
            self.remove_position_from_cache()
            return {"status": "SUCCESS"}
        except self.client.exception as error:
            print(error)
            return self.handle_client_error(error, time.time())

    def handle_client_error(self, error, timer):
        parsed_error = self.client.error_handler(error, self.position_side, self.is_swap)
        print(parsed_error)
        self.log_message(f'{parsed_error["error"].upper()}', timer, 'error')
        return parsed_error
