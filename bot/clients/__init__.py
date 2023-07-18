from typing import List

from bingX import ClientError
from bingX.perpetual.v1 import Perpetual as BingXClient

from ..utils.credentials import Credentials


class Client:
    def __init__(self, credentials: Credentials = None):
        self.name = credentials.exchange
        self.public_key = credentials.public_key
        self.private_key = credentials.private_key
        self.access_token = credentials.access_token
        self.account_id = credentials.account_id
        self.client = self._get_wrapped_client()

    def __repr__(self):
        return 'Client here'

    def _get_wrapped_client(self):
        client_map = {
            "bingx": _BingXClientWrapper(BingXClient(self.public_key, self.private_key)),
        }

        return client_map[self.name]


class _BingXClientWrapper:
    def __init__(self, client):
        self.client = client
        self.exception = ClientError

    def __repr__(self):
        return 'BingX Client Wrapper'

    def get_asset_price(self, symbol) -> float:
        response = self.client.latest_price(symbol)
        return float(response['tradePrice'])

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

    def exit_position(self, symbol: str, position_id: str):
        return self.client.close_position(symbol, position_id)

    def error_handler(self, error, position_side, is_swap):
        if error.error_msg == 'position not exist':
            opposite_position = 'Long' if position_side == 'Short' else 'Short'
            position = position_side if not is_swap else opposite_position
            error_msg = f'NO {position.upper()} POSITION TO CLOSE'
        if error.error_code == 80012:
            error_msg = 'INSUFFICIENT FUNDS'
        return {'status': 'ERROR', 'error': error_msg.upper()}
