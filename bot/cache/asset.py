from .position import Position


class Asset:
    def __init__(self,
                 symbol: str = None,
                 position: Position = Position(),
                 leverage: int = 1,
                 margin_mode: str = None):
        self.symbol = symbol
        self.position = position
        self.leverage = leverage
        self.margin_mode = margin_mode

    def __repr__(self):
        return f'<{self.symbol} - {self.leverage}X>'
    def get_symbol(self) -> str:
        return self.symbol

    def get_position(self) -> Position:
        return self.position

    def get_leverage(self) -> int:
        return self.leverage

    def get_margin_mode(self) -> str:
        return self.margin_mode

    def set_position(self, position: Position) -> None:
        self.position = position

    def set_leverage(self, leverage: int) -> None:
        self.leverage = leverage

    def set_margin_mode(self, margin_mode: str) -> None:
        self.margin_mode = margin_mode
