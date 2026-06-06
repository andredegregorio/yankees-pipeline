import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, explode, udf
from pyspark.sql.types import IntegerType

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


df = spark.read.json("s3://yankees-pipeline-andre/raw/player_info/2026-05-22/")

df = df.select(explode(col("people")).alias("player"))

df = df.select(
    col("player.id").alias("mlb_id"),
    col("player.firstName").alias("first_name"),
    col("player.lastName").alias("last_name"),
    col("player.birthDate").alias("birthdate"),
    col("player.batSide.code").alias("bats"),
    col("player.pitchHand.code").alias("throws"),
    col("player.weight").alias("weight"),
    col("player.primaryPosition.abbreviation").alias("position"),
    col("player.draftYear").alias("draft_year"),
    col("player.height").alias("height_raw")
)

def parse_height(height_str):
    if not height_str:
        return None
    parts = height_str.replace('"', '').split("' ")
    return int(parts[0]) * 12 + int(parts[1])
parse_height_udf = udf(parse_height, IntegerType())

df = df.withColumn("height_inches", parse_height_udf(col("height_raw")))
df = df.drop("height_raw")

df.write.mode("overwrite").parquet("s3://yankees-pipeline-andre/transformed/parquet/players/")

job.commit()