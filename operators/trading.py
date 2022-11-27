import pandas as pd
import numpy as np
import boto3
from datetime import datetime, timedelta
import ccxt
import pickle
import io
import xgboost as xgb
# from sklearn.model_selection import train_test_split

def pd_read_s3_parquet(key, bucket, s3_client=None, **args):
    if s3_client is None:
        s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(io.BytesIO(obj['Body'].read()), **args)

def pd_read_s3_multiple_parquets(filepath, bucket, s3=None, 
                                 s3_client=None, verbose=False, **args):
    if not filepath.endswith('/'):
        filepath = filepath + '/'  # Add '/' to the end
    if s3_client is None:
        s3_client = boto3.client('s3')
    if s3 is None:
        s3 = boto3.resource('s3')
    s3_keys = [item.key for item in s3.Bucket(bucket).objects.filter(Prefix=filepath)
               if item.key.endswith('.parquet')]
    if not s3_keys:
        print('No parquet found in', bucket, filepath)
    elif verbose:
        print('Load parquets:')
        for p in s3_keys: 
            print(p)
    dfs = [pd_read_s3_parquet(key, bucket=bucket, s3_client=s3_client, **args) 
           for key in s3_keys]
    return pd.concat(dfs, ignore_index=True)

class XGB_Trader():
    def load_model(self, aws_access_key_id, aws_secret_access_key, bucket_name, model_name):
        s3 = boto3.client('s3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        obj = s3.get_object(Bucket=bucket_name, Key=f'data/models/{model_name}')['Body']
        model = pickle.loads(obj.read())
        return model
    
    def predict(self, aws_access_key_id, aws_secret_access_key, bucket_name, model_name, **context):
        ts = context['ts']
        dtime = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S%z')

        model = self.load_model(aws_access_key_id, aws_secret_access_key, bucket_name, model_name)
        data = self.load_ccxt(dtime)
        X, y = data.drop(['datetime', 'close'], axis=1), data['close']
        pred = model.predict(X)
        print(f"actual: {y}, predict: {pred}")
    
    def load_ccxt(self, dtime: datetime):
        binance = ccxt.binance()
        btc_ohlcv = binance.fetch_ohlcv("BTC/USDT", timeframe='1m', since=int(dtime.timestamp() * 1000),limit=10)
        return pd.DataFrame(btc_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])

    def train(self, aws_access_key_id, aws_secret_access_key, bucket_name, model_name, **context):
        s3_client = boto3.client('s3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        s3 = boto3.resource('s3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        # load data
        execution_date = context['execution_date']
        df = pd.DataFrame()
        for td in range(19, -1, -1): # 20일치 데이터로 학습
            dt = execution_date - timedelta(days=td)
            path = f'data/parquet/{datetime.strftime(dt, "%Y-%m-%d")}'
            print(f"Reading {path} ...")
            temp_df = pd_read_s3_multiple_parquets(path, bucket_name, s3=s3, s3_client=s3_client)
            df = df.append(temp_df)
        
        # preprocess
        X, y = df.drop(['datetime', 'close'], axis=1), df['close']

        # train
        model = xgb.XGBRegressor(n_estimators=300)
        model.fit(X, y)

        # save model
        uploadBytesStream = bytes(pickle.dumps(model))
        s3_client.put_object(
            Bucket=bucket_name,
            Key=f'data/models/xgb:latest',
            Body=uploadBytesStream
        )
