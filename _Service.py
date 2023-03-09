from bingX.perpetual.v2 import Perpetual


class PerpetualService:
    open_orders = []

    def __init__(self,
                 client: Perpetual,
                 symbol: str,
                 order_type: str,
                 side: str,
                 position_side: str,
                 quantity: float,
                 margin: str,
                 leverage: int):
        self.client = client
        self.symbol = self._set_split_symbol(symbol)
        self.type = order_type
        self.side = side
        self.position_side = position_side
        self.quantity = quantity #self._set_asset_quantity(quantity)
        self.margin = margin
        self.leverage = leverage

    def _set_split_symbol(self, symbol: str, quote: str = 'USDT'):
        symbol_length = len(symbol)
        quote_length = len(quote)
        middle = symbol_length - quote_length

        return symbol[:middle] + "-" + symbol[middle:]

    def _set_asset_quantity(self, quantity: float):
        response = self.client.latest_price(self.symbol)
        asset_price = float(response['price'])

        return quantity / asset_price

    def set_margin_mode(self):
        if self.margin == 'ISOLATED' or self.margin == 'ISOLATED':
            self.client.switch_margin_mode(self.symbol, self.margin)

    def set_leverage(self):
        self.client.switch_leverage(self.symbol, 'LONG', self.leverage)
        self.client.switch_leverage(self.symbol, 'SHORT', self.leverage)

    def get_oder(self):
        return self.client.order(self.symbol, self.orderId)

    def open_trade(self):
        self.set_leverage()
        self.set_margin_mode()
        return self.client.trade_order(symbol=self.symbol,
                                       type=self.type,
                                       side=self.side,
                                       positionSide=self.position_side,
                                       quantity=self.quantity)

    def close_trade(self):
        return self.get_oder()
