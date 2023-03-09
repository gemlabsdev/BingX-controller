import time
import keys
import json
from botLogger import logger
from flask import Flask, request
from bingX.perpetual.v1 import Perpetual


from Service import PerpetualService

app = Flask(__name__)

publicKey = keys.public
secretKey = keys.secret
client_perpetual = Perpetual(publicKey, secretKey)
# client_perpetual.headers = {'X-BX-APIKEY': client_perpetual.api_key}
open_orders = []


@app.route('/perpetual/settings', methods=['POST'])
@app.route('/perpetual/trade', methods=['POST'])
def perpetual_order():
    data = json.loads(request.data)
    service = PerpetualService(client=client_perpetual,
                               symbol=data['symbol'],
                               side=data['side'],
                               action=data['action'],
                               quantity=data['quantity'],
                               trade_type=data['trade_type'],
                               margin=data['margin'],
                               leverage=data['leverage'] or 1)
    if data['action'] == 'Open':
        return service.open_trade()
    if data['action'] == 'Close':
        return service.close_trade()


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)

