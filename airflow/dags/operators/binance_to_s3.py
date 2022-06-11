import json
from io import StringIO
import pandas as pd
import ccxt
import boto3

def extract(aws_access_key_id, aws_secret_access_key, bucket_name, **context):
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
    print("Extractied Binance data!")

    uploadByteStream = bytes(json.dumps(markets).encode('UTF-8'))
    s3.put_object(
        Bucket=bucket_name,
        Key=f'raw/binance_data_{dt}.json',
        Body=uploadByteStream)
    print("Put Object to S3!")

def transform_and_load(aws_access_key_id, aws_secret_access_key, bucket_name, **context):
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
        Key=f"raw/binance_data_{dt}.json")['Body']
    print("Import Complete!")

    data = json.loads(obj.read().decode('utf-8'))
    print("data", type(data), data)
    df = pd.DataFrame(transform_binance_data(data),  columns=[0]).T
    print("df", df)
    print("Transform Complete!")

    csv_buffer = StringIO()
    df.to_csv(csv_buffer)

    s3.put_object(
        Bucket=bucket_name,
        Key=f'csv/binance_data_{dt}.csv',
        Body=csv_buffer.getvalue())
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