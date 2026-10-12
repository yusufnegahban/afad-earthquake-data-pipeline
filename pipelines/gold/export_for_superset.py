# Goal: Export Silver Delta Table to CSV for Superset
# Gold: Prepare clean data for dashboards / analytics

from pyspark.sql import SparkSession
import os


# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Earthquake_Gold_Export") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ACCESS_KEY"]) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_SECRET_KEY"]) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()


# Paths
silver_path = "s3a://afad-earthquakes/delta/afad_quakes_silver"
gold_csv_path = "s3a://afad-earthquakes/gold/earthquake_gold"


# 1. Read Silver Layer
df_gold = spark.read.format("delta").load(silver_path)

print(f"Loaded {df_gold.count()} rows from Silver Layer")


# 2. Prepare data for Superset
df_final = df_gold.select(
    "timestamp_ts",
    "cleaned_timestamp",
    "magnitude",
    "latitude",
    "longitude",
    "depth_km",
    "severity_class",
    "location"
)


# 3. Export to CSV
df_final.coalesce(1) \
    .write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(gold_csv_path)


print(f"Gold Layer exported to: {gold_csv_path}")


spark.stop()