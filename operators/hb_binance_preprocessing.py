import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

if __name__ == "__main__":
    """
        Usage: read from s3
    """
    base_dt = sys.argv[1]
    base_hr = sys.argv[2] if sys.argv[2] != "00" else "24"
    spark = SparkSession\
        .builder\
        .appName("ReadFromS3")\
        .getOrCreate()

    emp_RDD = spark.sparkContext.emptyRDD()
    columns = StructType([
            StructField('datetime', StringType(), True),
            StructField('open', StringType(), True),
            StructField('high', StringType(), True),
            StructField('low', StringType(), True),
            StructField('close', StringType(), True),
            StructField('volume', StringType(), True),
            ]
            )
    
    # Create an empty RDD with expected schema
    df = spark.createDataFrame(data = emp_RDD,
                            schema = columns)
    
    for hr in range(24):
        if f"{hr:02}" == base_hr:
            break
        s3_path = f's3://pipeliner-hb/data/parquet/{base_dt}/{base_dt} {hr:02}:00:00+00:00.parquet'
        print("Reading from ", s3_path, " ...")
        temp_df = spark.read.parquet(s3_path)
        df = df.union(temp_df)

    max_value = df.agg({"high": "max"}).collect()[0][0]
    min_value = df.agg({"low": "min"}).collect()[0][0]
    open_value = df.where(col('datetime').like("%00:00:00")).select("open").collect()[0][0]
    try:
        close_value = df.where(col('datetime').like("%23:59:00")).select("close").collect()[0][0]
    except:
        close_value = None
    volume = df.agg({"volume":"sum"}).collect()[0][0]

    text = f"O: {open_value} H: {max_value} L: {min_value} C: {close_value} V: {volume}" 
    print(text)
    rdd = spark.sparkContext.parallelize(text)
    rdd.saveAsTextFile(f"s3://pipeliner-hb/data/binance_statistics/{base_dt}_{base_hr}_ohlcv.txt")

    spark.stop()
