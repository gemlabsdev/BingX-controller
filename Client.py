from bingX.perpetual.v2 import Perpetual
from bingX.spot import Spot


class Client:
    def __init__(self, public_key, secret_key):
        self.public_key = public_key
        self.secret_key = secret_key
        self.perpetual = Perpetual(public_key, secret_key)
        self.spot = Spot(self.public_key, self.secret_key)
        self.perpetual.headers = {'X-BX-API_key': self.perpetual.api_key}
        print(self.perpetual)

