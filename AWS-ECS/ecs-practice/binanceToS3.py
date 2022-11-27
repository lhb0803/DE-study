import json
import pandas as pd
import ccxt
import boto3
from datetime import datetime

with open('./rootkey.csv', 'r') as f:
    aws_access_key_id, aws_secret_access_key = f.read().split('\n')
    aws_access_key_id = aws_access_key_id.split('=')[1]
    aws_secret_access_key = aws_secret_access_key.split('=')[1]

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
    )

print("Import Complete!")
now = datetime.now()
print(now)

binance = ccxt.binance()
markets = binance.fetch_ticker('ETH/BTC')

print("ccxt usage Complete!")
uploadByteStream = bytes(json.dumps(markets).encode('UTF-8'))

dt = f"{now.year}-{now.month:02}-{now.day:02}"
s3.put_object(Bucket='binance-raw-by-ecs',
    Key=f'{dt}/test.json',
    Body=uploadByteStream)
print("Put Object Complete!")