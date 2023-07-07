# BingX-controller
A controller for routing webhook trading signals to the BingX API

To run it just install the python requirements and node modules, build the frontend, and run the application using ```python app.py```

## Endpoints and request bodies

<details><summary>/perpetual/trade</summary>
<p></p>
Handles opening and closing of Long and Short positions. "quantity" is in USDT
<p></p>
Open a Long

``` json
{
    "symbol": "BTCUSDT",
    "action": "Open", 
    "side": "Bid",
    "trade_type": "Market",
    "quantity": 10.0
}
```
Close a Long

``` json
{
    "symbol": "BTCUSDT",
    "action": "Close", 
    "side": "Bid",
    "trade_type": "Market",
    "quantity": 10.0
}
```
 
Open a Short
``` json
{
    "symbol": "BTCUSDT",
    "action": "Open", 
    "side": "Ask",
    "trade_type": "Market",
    "quantity": 10.0
}
```

Close a Short
``` json
{
    "symbol": "BTCUSDT",
    "action": "Close", 
    "side": "Ask",
    "trade_type": "Market",
    "quantity": 10.0
}
```
</details>
<details><summary>/perpetual/leverage</summary>
<p></p>
Changes the leverage for the symbol sent in the request body

``` json
{
    "symbol": "BTCUSDT",
    "leverage": 5
}
```
</details>
<details><summary>/keys</summary>
<p></p>
Keys can be stored locally in a file called keys.py and added to the project before deploment. The keys can also be overriden/set using the /keys endpoint

``` json
{
    "public": "public",
    "private": "private"
}
```
</details>

