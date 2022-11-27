import sys
from random import random
from operator import add

from pyspark.sql import SparkSession


if __name__ == "__main__":
    """
        Usage: read from s3
    """
    spark = SparkSession\
        .builder\
        .appName("ReadFromS3")\
        .getOrCreate()

    df = spark.read.parquet('s3://pipeliner-hb/data/parquet/20220625.parquet')
    rows = df.count()
    print(f"Rows count: {rows}")
