import subprocess
import time
import os

SPARK_SUBMIT = "/opt/spark/bin/spark-submit"

JARS = (
    "/opt/spark/extra-jars/io.delta_delta-spark_2.12-3.2.0.jar,"
    "/opt/spark/extra-jars/io.delta_delta-storage-3.2.0.jar,"
    "/opt/spark/extra-jars/org.apache.hadoop_hadoop-aws-3.3.4.jar,"
    "/opt/spark/extra-jars/com.amazonaws_aws-java-sdk-bundle-1.12.262.jar"
)

JOBS = [
    ("/opt/spark/jobs/silver/spark_clean.py", "Silver"),
    ("/opt/spark/jobs/gold/export_for_superset.py", "Gold"),
]

env = os.environ.copy()
env["PYTHONPATH"] = (
    "/opt/spark/jobs/silver:"
    "/opt/spark/jobs/gold:"
    "/usr/local/lib/python3.10/site-packages"
)

while True:
    print("\n=== PIPELINE RUN STARTED ===", flush=True)

    for job, name in JOBS:
        print(f"=== Running {name} ===", flush=True)

        result = subprocess.run(
            [SPARK_SUBMIT, "--jars", JARS, job],
            env=env
        )

        if result.returncode != 0:
            print(f"!!! {name} FAILED !!!", flush=True)
            break

        print(f"=== {name} completed ===", flush=True)

    print("=== PIPELINE RUN FINISHED ===", flush=True)
    print("Sleeping 300 seconds...", flush=True)

    time.sleep(300)