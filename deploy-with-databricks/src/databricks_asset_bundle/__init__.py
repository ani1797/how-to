def hello(name: str = None) -> str:
    return f"Hello from {'Unknown' if not name else name}!"


def get_spark():
    """
    Get the current Spark session.
    """
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    return spark
