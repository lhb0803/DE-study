import requests
from datetime import datetime, timedelta, timezone
import json
import argparse
import boto3
import os

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
    url = f"{SERVER_URL}/v1/candles/minutes/1?unit=1&market={market}&to={dtime}&count={count}"
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

def put_s3(aws_access_key, aws_secret_key, bucket_name, file_name, data):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    s3.put_object(
        Bucket=bucket_name,
        Key=f'{file_name}.json',
        Body=bytes(json.dumps(data).encode('UTF-8'))
    )
    print("put s3")


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument("--m", help="which market and which crypto", type=str)
    argp.add_argument("--t", help="datetime format: '%Y-%m-%d %H:%M:%S'", type=str)
    argp.add_argument("--c", help="how many ticks", type=int)

    args = argp.parse_args()
    candles = get_ohlcv(args.m, args.t, args.c)
    candle_type_list = [get_candle_type(candle) for candle in candles]

    print(f"Candles Count: {len(candle_type_list)}")
    print(f"Lastet Candle: {candle_type_list[-1]}")

    aws_access_key = os.environ['AWS_ACCESS_KEY']
    aws_secret_key = os.environ['AWS_SECRET_KEY']
    put_s3(aws_access_key, aws_secret_key, 'hb-operator-test', f'{args.t} candle', candle_type_list)

if __name__ == "__main__":
    main()