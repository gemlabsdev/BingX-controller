class Credentials:
    def __init__(self, public_key, private_key, exchange):
        self.public_key = public_key
        self.private_key = private_key
        self.exchange = exchange

    def __repr__(self):
        return f'<{self.exchange.upper()} credentials>'
