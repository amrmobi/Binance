import websocket, json, pprint, talib, numpy, mysql.connector, time
import config, db_config
from binance.client import Client
from binance.enums import *


SOCKET = "wss://stream.binance.com:9443/ws/etcusdt@kline_1m"

RSI_PERIOD = 4
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETCUSD'
TRADE_QUANTITY = 0.05

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    # print('received message')
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    # is_candle_closed = True

    if is_candle_closed:

        time1 = json_message['E']
        open = candle['o']
        high = candle['h']
        low = candle['l']
        close = candle['c']
        volume = candle['n']

        # print (time)
        # print (open)
        # print (high)
        # print (low)
        # print (close)
        # print (volume)

        mycursor = db_config.mydb.cursor()
        # mycursor1 = db_config.mydb.cursor()

        sql = """INSERT INTO eth_usd (timestamp, ticket, price, volume) VALUES (%s, %s, %s, %s)"""

        data = (time1, "ETH", close, volume)

        mycursor.execute (sql, data)

        db_config.mydb.commit()

        # print(mycursor.rowcount, "record inserted.")

        time.sleep(5)

        mycursor.execute("SELECT * FROM eth_usd ORDER BY TIMESTAMP DESC LIMIT 1")

        # mycursor1.execute("SELECT count(*) FROM eth_usd")

        # myresult = mycursor.fetchall()

        # for x in myresult:
        #     print(x)

        myresult = mycursor.fetchone()

        myresult = str(myresult).replace("(", "")
        myresult = str(myresult).replace(")", "")
        myresult = str(myresult).replace(",", "")

        print(myresult) 

        # print("candle closed at {}".format(close))
        closes.append(float(close))
        # print("closes")
        print(closes)

        # if len(closes) > RSI_PERIOD:
        #     np_closes = numpy.array(closes)
        #     rsi = talib.RSI(np_closes, RSI_PERIOD)
        #     print("all rsis calculated so far")
        #     print(rsi)
        #     last_rsi = rsi[-1]
        #     print("the current rsi is {}".format(last_rsi))

        #     if last_rsi > RSI_OVERBOUGHT:
        #         if in_position:
        #             print("Overbought! Sell! Sell! Sell!")
        #             # put binance sell logic here
        #             order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
        #             if order_succeeded:
        #                 in_position = False
        #         else:
        #             print("It is overbought, but we don't own any. Nothing to do.")
            
        #     if last_rsi < RSI_OVERSOLD:
        #         if in_position:
        #             print("It is oversold, but you already own it, nothing to do.")
        #         else:
        #             print("Oversold! Buy! Buy! Buy!")
        #             # put binance buy order logic here
        #             order_succeeded = order(SIDE_BUY, 0.99900000, TRADE_SYMBOL)
        #             if order_succeeded:
        #                 in_position = True

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()