from pyspark.sql import SparkSession
from pipelines.silver.transformations import filter_valid_magnitudes
import os
from pyspark.sql.functions import col, to_timestamp, when, row_number
from pyspark.sql.window import Window
from delta.tables import DeltaTable
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder \
    .appName("Earthquake_Silver_Cleaning") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ACCESS_KEY"]) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_SECRET_KEY"]) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .getOrCreate()

minio_endpoint = "http://minio:9000"
minio_access_key = os.environ["MINIO_ACCESS_KEY"]
minio_secret_key = os.environ["MINIO_SECRET_KEY"]

spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", minio_endpoint)
spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", minio_access_key)
spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", minio_secret_key)
spark._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
spark._jsc.hadoopConfiguration().set("fs.s3a.ssl.enabled", "false")

bronze_path = "s3a://afad-earthquakes/afad/"
silver_path = "s3a://afad-earthquakes/delta/afad_quakes_silver"

bronze_schema = StructType([
    StructField("timestamp_ts", StringType(), True),
    StructField("magnitude", DoubleType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("depth_km", DoubleType(), True),
    StructField("location", StringType(), True),
    StructField("source_url", StringType(), True),
    StructField("ingested_at", StringType(), True)
])

print("Starting Silver Layer data cleaning process...")

try:

    df_bronze = (
        spark.read
        .format("json")
        .schema(bronze_schema)
        .option("multiLine", "true")
        .option("recursiveFileLookup", "true")
        .load(bronze_path)
    )

    print(f"Bronze records: {df_bronze.count()}")

    df_transformed = (
    df_bronze
    .transform(filter_valid_magnitudes)
    .withColumn(
        "cleaned_timestamp",
        to_timestamp(col("timestamp_ts"))
    )
        )
    .withColumn(
            "severity_class",
            when(col("magnitude") >= 5, "High")
            .when(col("magnitude") >= 3, "Medium")
            .otherwise("Low")
        )
        .select(
            "timestamp_ts",
            "magnitude",
            "latitude",
            "longitude",
            "depth_km",
            "location",
            "cleaned_timestamp",
            "severity_class",
            "source_url",
            "ingested_at"
        )
    )

    print(
        f"Clean records before deduplication: "
        f"{df_transformed.count()}"
    )

    key_columns = [
        "timestamp_ts",
        "latitude",
        "longitude",
        "location"
    ]

    window_spec = (
        Window
        .partitionBy(*key_columns)
        .orderBy(col("ingested_at").desc())
    )

    df_transformed = (
        df_transformed
        .withColumn(
            "_row_number",
            row_number().over(window_spec)
        )
        .filter(col("_row_number") == 1)
        .drop("_row_number")
    )

    print(
        f"Clean records after global deduplication: "
        f"{df_transformed.count()}"
    )

    if not DeltaTable.isDeltaTable(spark, silver_path):

        print("Creating Silver Delta Table...")

        (
            df_transformed.write
            .format("delta")
            .option("mergeSchema", "true")
            .mode("overwrite")
            .save(silver_path)
        )

        print("Silver Layer created successfully.")

    else:

        print("Updating Silver Delta Table...")

        delta_table = DeltaTable.forPath(
            spark,
            silver_path
        )

        (
            delta_table.alias("target")
            .merge(
                df_transformed.alias("source"),
                """
                target.timestamp_ts = source.timestamp_ts
                AND target.latitude = source.latitude
                AND target.longitude = source.longitude
                AND target.location = source.location
                """
            )
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )

        print("Silver merge completed.")

except Exception as e:

    print(f"Silver Layer error: {e}")

finally:

    print("Stopping Spark session.")
    spark.stop()