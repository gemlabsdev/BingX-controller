import json
from Key import Key
from Cache import Cache
from flask import Flask, request
from bingX.perpetual.v1 import Perpetual
from Service import PerpetualService

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'BING-X CONTROLLER BY BREADGINEER'


@app.route('/keys', methods=['POST'])
def override_keys():
    data = json.loads(request.data)
    Key.public_key = data['public']
    Key.secret_key = data['private']

    return json.dumps({'status': 'SUCCESS'})


@app.route('/keys', methods=['GET'])
def view_keys():
    keys = {'public': Key.public_key,
            'secret': Key.secret_key}
    return json.dumps(keys)


@app.route('/perpetual/trade', methods=['POST'])
def perpetual_order():
    client = Perpetual(Key.public_key, Key.secret_key)
    data = json.loads(request.data)
    service = PerpetualService(client=client,
                               symbol=data['symbol'],
                               side=data['side'],
                               action=data['action'],
                               quantity=data['quantity'],
                               trade_type=data['trade_type'])
    if data['action'] == 'Open':
        return service.open_trade()
    if data['action'] == 'Close':
        return service.close_trade()


@app.route('/perpetual/leverage', methods=['POST'])
def change_leverage():
    client = Perpetual(Key.public_key, Key.secret_key)
    data = json.loads(request.data)
    service = PerpetualService(client=client,
                               symbol=data['symbol'],
                               leverage=data['leverage'])
    service.set_leverage()
    return f'{{"symbol":"{service.symbol}", "leverage":"{service.leverage}"}}'


if __name__ == '__main__':
    from waitress import serve
    serve(app)
