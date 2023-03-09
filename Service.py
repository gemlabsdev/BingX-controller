from bingX.perpetual.v1 import Perpetual
from botLogger import logger


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
        self.position_side = "LONG" if self.side == 'Bid' else 'SHORT'

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
        logger.info(f'Requesting open {self.symbol} positions from BingX')
        response = self.client.positions(self.symbol)
        if response['positions'] is None:
            return
        return response['positions'][0]

    def open_trade(self):
        self.close_trade(isOnlyClose=False)
        logger.info(f'Opening new {self.position_side} for {self.symbol}')
        return self.client.place_order(symbol=self.symbol,
                                       side=self.side,
                                       action=self.action,
                                       entrustPrice=self.entrust_price,
                                       entrustVolume=self.entrust_volume,
                                       tradeType=self.trade_type)

    def close_trade(self, isOnlyClose=True):
        positions = self.get_open_position()
        if positions is None:
            logger.info(f'No open positions for {self.symbol}')
            return 'NONE'
        position_side = positions['positionSide']
        position_id = positions['positionId']
        if not isOnlyClose:
            logger.warn(f'Open position found - Only 1 open position per symbol allowed')
        logger.info(f'Closing {position_side.upper()} position for {self.symbol}')
        return self.client.close_position(symbol=self.symbol, positionId=position_id)
