
"""
Earthquake Data Transformations

Purpose:
    Keep reusable data-cleaning rules separate from pipeline execution.

Rule:
    Accept earthquake records only when magnitude is not null
    and greater than zero.

Usage:
    The Silver pipeline and automated tests can use the same
    function to avoid duplicating the filtering rule.
"""

from pyspark.sql.functions import col


def filter_valid_magnitudes(df):
    """Return records with a non-null, positive earthquake magnitude."""
    return df.filter(
        col("magnitude").isNotNull()
        & (col("magnitude") > 0)
    )
