from typing import List

from .asset import Asset


class Exchange:

    def __init__(self, name: str = None, assets: List[Asset] = None):
        self.name = name
        self.assets = assets

    def __repr__(self):
        return f'<{self.name.upper()}: {self.assets}>'

    def get_name(self) -> str:
        return self.name

    def get_assets(self) -> List[Asset]:
        return self.assets

    def set_name(self, name: str) -> None:
        self.name = name

    def append_asset(self, asset: Asset) -> None:
        self.assets.append(asset)

    def find_asset(self, symbol: str) -> Asset:
        return next(filter(lambda _asset: _asset.get_symbol() == symbol, self.assets), None)
        
