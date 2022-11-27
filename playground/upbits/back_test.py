from upbits.upbit_orders import *
from datetime import datetime, timedelta, timezone
import time
from typing import Callable


def backtest(end_datetime: datetime, strategy: Callable, market='KRW-BTC', init_volume = 1.0, init_account = 0.0) -> None:
    while(datetime.now(tz=KST) < end_datetime and init_volume > 0 and init_account >= 0):
        now_datetime = datetime.now(tz=KST)
        print(datetime.strftime(now_datetime, '%Y-%m-%d %H:%M:%S'))
        candle = get_ohlcv(market=market, 
            dtime=datetime.strftime(now_datetime, '%Y-%m-%d %H:%M:%S'),
            count=1)[0]
        
        print(f"close: {candle['close']} Won")
        result = strategy(candle)
        if result[0] == 1 and init_account >= result[1] * candle['close']: # Buy
            print(f"Buy!\n {result[1]} x {candle['close']} Won")
            init_volume += result[1]
            init_account -= result[1] * candle['close']

        elif result[0] == -1 and init_volume >= result[1]: # Sell
            print(f"Sell!\n {result[1]} x {candle['close']} Won")
            init_volume -= result[1]
            init_account += result[1] * candle['close']
        
        else:
            print("Stay!")

        print(f"account: {init_account} Won")
        time.sleep(60)


def candle_buy_and_sell(candle: dict, p=0.5) -> tuple:
    color, stick_len = get_candle_type(candle, p=p)
    if color and stick_len: # Blue Long -> Buy
        return (1, 0.01)
    elif not color and stick_len: # Red Long -> Sell
        return (-1, 0.01)
    else:
        return (0, 0)


if __name__ == "__main__":
    end_datetime = datetime.now(tz=KST) + timedelta(minutes=5) #datetime(2022, 10, 2, 10, 8, 0, tzinfo=KST)
    backtest(end_datetime=end_datetime, strategy=candle_buy_and_sell, init_account=1000000)
