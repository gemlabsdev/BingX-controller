class Cache:
    open_positions = {'XXX-USDT': {'positionId': None,
                                   'positionSide': None}
                      }
    symbol_leverage = {'XXX-USDT': 1}

    @staticmethod
    def clear_cache():
        Cache.open_positions = {'XXX-USDT': {'positionId': None,
                                             'positionSide': None}
                                }
        Cache.symbol_leverage = {'XXX-USDT': 1}
