import json
import time

from ..utils.logger import logger
from ..cache import Cache, Position


def stop_timer(time_start):
    return int((time.time() - time_start) * 1000)


class BaseOrderService:
    open_position = None

    def __init__(self,
                 client: any = None,
                 symbol: str = None,
                 agent: str = None,  # 'exchange', 'broker'
                 side: str = None,  # 'buy', 'sell'
                 action: str = None,  # 'open', 'close'
                 quantity: float = 0,
                 trade_type: str = 'market',  # 'market', 'limit'
                 margin: str = 'isolated',  # 'isolated', 'cross'
                 leverage: int = 1,
                 safety: bool = False
                 ):
        self.client = client
        self.symbol = symbol
        self.agent = agent
        self.side = side
        self.opposite_side = "sell" if self.side == 'buy' else 'buy'
        self.action = action
        self.trade_type = trade_type
        self.entrust_price = 0
        self.leverage = leverage
        self.quantity = quantity * self.leverage
        self.amount = self._set_amount()
        self.margin = margin
        self.position_side = "LONG" if self.side == 'buy' else 'SHORT'
        self.safety = safety
        self.is_swap = False

    def _set_amount(self):
        return self.client.get_order_amount(self.symbol, self.quantity)

    def set_margin_mode(self):
        self.client.change_margin_mode(self.symbol, self.margin)

    def set_leverage(self):
        self.client.change_leverage(self.symbol, self.leverage)

    def fetch_open_position(self) -> Position:
        response = self.client.get_open_positions(self.symbol)
        if api_positions := response['positions']:
            return Position(api_positions[0]['positionId'], api_positions[0]['positionSide'])


    def log_message(self, message, timer, level='info'):
        if level == 'error':
            logger.error(f'{self.agent.upper()} - {self.symbol} - {message} - {stop_timer(timer)}ms')
            return

        logger.info(f'{self.agent.upper()} - {self.symbol} - {message} - {stop_timer(timer)}ms')

    def start_order(self):
        timer = time.time()
        position = self.fetch_open_position()
        if self.action == 'close':
            safety_message = 'SAFETY HOOK - ' if self.safety else ''
            if position is None or position.get_side() != self.position_side:
                self.log_message(f'{safety_message}NO {self.position_side.upper()} POSITION TO CLOSE', timer)
                return json.dumps({'status': 'NOT_FOUND'})
            close_order = self.close_order(position.get_id())
            if close_order['status'] == 'ERROR':
                return close_order
            self.log_message(f'{safety_message}CLOSED {self.position_side} POSITION', timer)
            return json.dumps({'status': 'SUCCESS'})

        if self.action == 'open':
            if position is None:
                open_order = self.open_order()
                if open_order['status'] == 'ERROR':
                    return open_order
                self.log_message(f'OPENED {self.position_side} POSITION', timer)
                return json.dumps({'status': 'SUCCESS'})
            if position.get_side() == self.position_side:
                self.log_message(f'{self.position_side} POSITION ALREADY IN PLACE', timer)
                return {'status': 'SAME_DIRECTION'}
            if position.get_side() != self.position_side:
                close_order = self.close_order(position.get_id())
                if close_order['status'] == 'ERROR':
                    return close_order
                opposite_position = 'LONG' if self.position_side == 'SHORT' else 'SHORT'
                self.log_message(f'CLOSED EXISTING {opposite_position.upper()} POSITION', timer)
                open_order = self.open_order()
                if open_order['status'] == 'ERROR':
                    return open_order
                self.log_message(f'OPENED {self.position_side} POSITION', timer)
                return json.dumps({'status': 'SUCCESS'})

    def open_order(self):
        try:
            self.set_leverage()
            self.set_margin_mode()
            time.sleep(0.1)
            response = self.client.enter_position(symbol=self.symbol,
                                                  trade_type=self.trade_type,
                                                  side=self.side,
                                                  amount=self.amount,
                                                  position_side=self.position_side)
            time.sleep(0.1)
            return {"status": "SUCCESS"}

        except self.client.exception as error:
            print(error)
            return self.handle_client_error(error, time.time())

    def close_order(self, position_id: str) -> object:
        try:
            time.sleep(0.2)
            self.client.exit_position(symbol=self.symbol,
                                      trade_type=self.trade_type,
                                      side=self.side,
                                      amount=self.amount,
                                      position_id=position_id,
                                      quantity=self.quantity)
            return {"status": "SUCCESS"}
        except self.client.exception as error:
            return self.handle_client_error(error, time.time())

    def handle_client_error(self, error, timer):
        parsed_error = self.client.error_handler(error, self.position_side, self.is_swap)
        self.log_message(f'{parsed_error["error"].upper()}', timer, 'error')
        return parsed_error
