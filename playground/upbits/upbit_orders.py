import jwt
import hashlib
import requests
import uuid
from urllib.parse import urlencode, unquote
from datetime import datetime, timedelta, timezone
import json
from getpass import getpass

ACCESS_KEY = getpass("ACCESS_KEY: ")
SECRET_KEY = getpass("SECRET_KEY: ")
SERVER_URL = 'https://api.upbit.com'

KST = timezone(timedelta(hours=9))

def get_candle_type(candle: dict, p=0.8) -> list:
    """
    Return Sticks
    `[False, False]`: Red Short Stick
    `[False, True]`: Red Long Stick
    `[True, False]`: Blue Short Stick
    `[True, True]`: Blue Long Stick

    [reference](https://stockmong.tistory.com/m/27)
    """
    shadow_len = candle['high'] - candle['low']
    body_len = candle['close'] - candle['open']

    return [body_len > 0, body_len **2 > (shadow_len * p) **2]

def get_ohlcv(market:str, dtime: str, count=1) -> list:
    url = f"https://api.upbit.com/v1/candles/minutes/1?unit=1&market={market}&to={dtime}&count={count}"
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    resp_list = json.loads(response.text)
    ohlcv_list = []
    for tick in resp_list:
        ohlcv_list.append(
            {
                'timestamp': tick['timestamp'],
                'open': tick['opening_price'],
                'high': tick['high_price'],
                'low': tick['low_price'],
                'close': tick['trade_price'],
                'volume': tick['candle_acc_trade_volume'],
            }
        )
    ohlcv_list.reverse()
    return ohlcv_list


if __name__ == "__main__":
    symbol = 'KRW-BTC'
    dtime = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    candles = get_ohlcv(market=symbol, dtime=dtime, count=5)
    for candle in candles:
        print(f"""
dtime: {datetime.fromtimestamp(candle['timestamp']/1000, tz=KST)}\n
open: {candle['open']}\n
high: {candle['high']}\n
low: {candle['low']}\n
close: {candle['close']}\n
volume: {candle['volume']}\n
            """)
        color, stick_len = get_candle_type(candle)
        if color: # Blue
            if stick_len: # Long
                print("Blue Long Stick")
            else: # Short
                print("Blue Short Stick")
        else: # Red
            if stick_len: # Long
                print("Red Long Stick")
            else: # Short
                print("Red Short Stick")

