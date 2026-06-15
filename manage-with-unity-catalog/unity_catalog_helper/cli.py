import os
import sys
import logging

from argparse import ArgumentParser, FileType

from pydantic_yaml import parse_yaml_file_as

from schema import ConfigSchema
from query_collector import QueryGenerator

def get_spark():
    from pyspark.sql import SparkSession
    from delta import configure_spark_with_delta_pip

    spark = configure_spark_with_delta_pip(
        SparkSession.builder.appName("unity-catalog-helper")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    ).getOrCreate()
    return spark

def get_dbutils(spark):
    try:
        from pyspark.dbutils import DBUtils
        dbutils = DBUtils(spark)
    except ImportError:
        try:
            import IPython
            dbutils = IPython.get_ipython().user_ns["dbutils"]
        except AttributeError:
            dbutils = None
    return dbutils

def default_config_file():
    current_dir = os.path.dirname(os.path.abspath("__file__"))
    filepath = os.path.abspath(os.path.join(current_dir, "config.yaml"))
    return filepath

def default_output_file():
    current_dir = os.path.dirname(os.path.abspath("__file__"))
    filepath = os.path.abspath(os.path.join(current_dir, "output.sql"))
    return filepath

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s')
    argparser = ArgumentParser()
    argparser.add_argument("-c", type=str, default=default_config_file(), help="path to config file")
    argparser.add_argument("-o", type=str, default=default_output_file(), help="path to output sql file")
    argparser.add_argument("-nc", help="Disables generation of SQL comments in the output file", action='store_true')
    argparser.add_argument("-ng", help="do not generate SQL ANSII DCL statements", action='store_true')
    argparser.add_argument("--dry-run", "-t", help="print output to stdout instead of writing to file", action='store_true')
    argparser.add_argument("--debug", help="Use only to debug the script", action='store_true')

    cfg = argparser.parse_args(sys.argv[1:])
    if cfg.debug: print(cfg)

    config = parse_yaml_file_as(ConfigSchema, cfg.c)
    if cfg.debug: print(config)

    spark = get_spark()
    dbutils = get_dbutils(spark)

    qg = QueryGenerator(spark, dbutils, no_grant = cfg.ng, debug = cfg.debug, no_comments = cfg.nc)
    
    for catalog in config.catalogs:
        qg.add_catalog(catalog)

    for table in config.tables:
        qg.add_table(table)

    if not cfg.dry_run:
        with open(cfg.o, "w+") as f:
            f.write(qg.get_queries())
    else:
        print(qg.queries)
