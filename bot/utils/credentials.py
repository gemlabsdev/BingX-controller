class Credentials:
    def __init__(self,
                 public_key: str = None,
                 private_key: str = None,
                 access_token: str = None,
                 account_id: str = None,
                 exchange: str = None,
                 ):
        self.public_key = public_key
        self.private_key = private_key
        self.access_token = access_token
        self.account_id = account_id
        self.exchange = exchange

    def __repr__(self):
        return f'<{self.exchange.upper()} credentials>'
