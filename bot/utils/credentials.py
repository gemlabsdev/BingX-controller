class ExchangeCredentials:
    def __init__(self,
                 public_key: str = None,
                 private_key: str = None,
                 ):
        self.public_key = public_key
        self.private_key = private_key


class BrokerCredentials:
    def __init__(self,
                 server: str = None,
                 account: str = None,
                 password: str = None,
                 ):
        self.server = server
        self.account = account
        self.password = password


class Credentials:
    def __init__(self,
                 name: str = None,
                 exchange_credentials: ExchangeCredentials = None,
                 broker_credentials: BrokerCredentials = None,
                 ):
        self.name = name
        self.exchange_credentials = exchange_credentials
        self.broker_credentials = broker_credentials

    def __repr__(self):
        return f'<{self.name.upper()} credentials>'
