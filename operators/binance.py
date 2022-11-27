import json
from io import BytesIO
import pandas as pd
import ccxt
import boto3
from datetime import datetime, timedelta

def extract_binance_daily(aws_access_key_id, aws_secret_access_key, bucket_name, **context):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
        )

    target_date = context['execution_date'].date()
    print(target_date)
    dt = f"{target_date.year}{target_date.month:02}{target_date.day:02}"

    binance = ccxt.binance()
    markets = binance.fetch_ticker('ETH/BTC')
    print("Extracted Binance data!")

    uploadByteStream = bytes(json.dumps(markets).encode('UTF-8'))
    s3.put_object(
        Bucket=bucket_name,
        Key=f'data/binance/{dt}.json',
        Body=uploadByteStream)
    print("Put Object to S3!")

def extract_binance_hourly(aws_access_key_id, aws_secret_access_key, bucket_name, **context):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
        )
    ts = context['ts']
    print(ts)
    target_dtime = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S%z') - timedelta(hours=0, minutes=5)
    print(f"target_dtime {target_dtime}")
    binance = ccxt.binance()
    btc_ohlcv = binance.fetch_ohlcv("BTC/USDT", timeframe='1m', since=int(target_dtime.timestamp() * 1000), limit=60)
    df = pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    out_buffer = BytesIO()
    df.to_parquet(out_buffer, index=False)

    s3.put_object(
        Bucket=bucket_name,
        Key=f'data/parquet/{target_dtime.date()}/{target_dtime}.parquet',
        Body=out_buffer.getvalue())

def transform_as_parquet(aws_access_key_id, aws_secret_access_key, bucket_name, **context):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
        )

    target_date = context['execution_date'].date()
    print(target_date)
    dt = f"{target_date.year}{target_date.month:02}{target_date.day:02}"

    obj = s3.get_object(
        Bucket=bucket_name, 
        Key=f"data/binance/{dt}.json")['Body']
    print("Import Complete!")

    data = json.loads(obj.read().decode('utf-8'))
    print("data", type(data), data)
    df = pd.DataFrame(transform_binance_data(data),  columns=[0]).T
    print("df", df)
    print("Transform Complete!")

    out_buffer = BytesIO()
    df.to_parquet(out_buffer, index=False)

    s3.put_object(
        Bucket=bucket_name,
        Key=f'data/parquet/{dt}.parquet',
        Body=out_buffer.getvalue())
    print("Put Object to S3!")

def transform_binance_data(data):
    sr = pd.Series()
    for key, value in data.items():
        print(f"{key}: {value}")
        if key != 'info':
            sr[key] = value
        else:
            for key2, value2 in value.items():
                if key == 'symbol': continue
                sr[key2] = value2
    
    return sr