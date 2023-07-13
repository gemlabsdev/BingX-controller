from .asset import Asset
from .exchange import Exchange
from .position import Position


class Cache:
    cache = []

    @classmethod
    def create_asset_cache(cls, exchange: str, symbol: str) -> None:
        _exchange = cls.get_exchange(exchange)
        if _exchange is None:
            cls.cache.append(Exchange(exchange, [Asset(symbol)]))
            return
        _asset = _exchange.find_asset(symbol)
        if _asset is None:
            _exchange.append_asset(Asset(symbol))
            return

    @classmethod
    def get_asset(cls, exchange, symbol) -> Asset:
        _exchange = cls.get_exchange(exchange)
        return _exchange.find_asset(symbol)

    @classmethod
    def get_asset_position(cls, exchange, symbol) -> Position:
        return cls.get_asset(exchange, symbol).get_position()

    @classmethod
    def get_asset_leverage(cls, exchange, symbol) -> int:
        return cls.get_asset(exchange, symbol).get_leverage()

    @classmethod
    def get_asset_margin(cls, exchange, symbol) -> str:
        return cls.get_asset(exchange, symbol).get_margin()

    @classmethod
    def set_asset_position(cls, exchange, symbol, position: Position) -> None:
        _position = cls.get_asset_position(exchange, symbol)
        _position.set_id(position.get_id())
        _position.set_side(position.get_side())

    @classmethod
    def remove_asset_position(cls, exchange, symbol) -> None:
        _position = cls.get_asset_position(exchange, symbol)
        _position.set_id()
        _position.set_side()

    @classmethod
    def set_asset_leverage(cls, exchange, symbol, leverage) -> None:
        cls.get_asset(exchange, symbol).set_leverage(leverage)

    @classmethod
    def set_asset_margin(cls, exchange, symbol, margin) -> None:
        cls.get_asset(exchange, symbol).set_margin(margin)

    @classmethod
    def get_exchange(cls, name: str) -> Exchange:
        return next(filter(lambda _exchange: _exchange.get_name() == name, cls.cache), None)

    @classmethod
    def clear_cache(cls) -> None:
        cls.cache = []
