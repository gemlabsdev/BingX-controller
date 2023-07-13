class Cache:
    positions = {
        'exchange': {
            'XXX-USDT': {
                'positionId': None,
                'positionSide': None,
                'leverage': 1
            }
        }
    }

    @staticmethod
    def clear_cache():
        Cache.positions = {
            'exchange': {
                'XXX-USDT': {
                    'positionId': None,
                    'positionSide': None,
                    'leverage': 1
                }
            }
        }
