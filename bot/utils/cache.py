import copy
class Cache:
    positions = {
        'exchange': {
            'XXX-USDT': {
                'position': {
                    'id': None,
                    'side': None,
                },
                'leverage': 1
            }
        }
    }

    @classmethod
    def create_symbol_cache(cls, exchange, symbol):
        if exchange not in cls.positions:
            cls.positions[exchange] = {}
        if symbol not in cls.positions[exchange]:
            cls.positions[exchange][symbol] = {
                'position': {
                    'id': None,
                    'side': None,
                },
                'leverage': 1
            }

    @classmethod
    def get_symbol_cache(cls, exchange, symbol):
        return cls.positions[exchange][symbol]

    @classmethod
    def get_symbol_position(cls, exchange, symbol):
        return cls.positions[exchange][symbol]['position']

    @classmethod
    def get_symbol_leverage(cls, exchange, symbol):
        return cls.positions[exchange][symbol]["leverage"]

    @classmethod
    def set_symbol_position(cls, exchange, symbol, position):
        cls.positions[exchange][symbol]["position"]["id"] = position["positionId"]
        cls.positions[exchange][symbol]["position"]["side"] = position["positionSide"]

    @classmethod
    def set_symbol_leverage(cls, exchange, symbol, leverage):
        cls.positions[exchange][symbol]["leverage"] = leverage

    @classmethod
    def clear_cache(cls):
        cls.positions = {
            'exchange': {
                'XXX-USDT': {
                    'positionId': None,
                    'positionSide': None,
                    'leverage': 1
                }
            }
        }
