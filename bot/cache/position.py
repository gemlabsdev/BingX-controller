class Position:
    def __init__(self, _id: str = None, side: str = None):
        self._id = _id
        self.side = side

    def __repr__(self):
        return f'<{self._id}>'

    def get_id(self) -> str:
        return self._id

    def get_side(self) -> str:
        return self.side

    def set_id(self, _id: str = None) -> None:
        self._id = _id

    def set_side(self, side: str = None) -> None:
        self.side = side
