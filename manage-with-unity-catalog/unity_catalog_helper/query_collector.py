import logging, pathlib, os

from urllib.parse import urlparse
from typing import List, Tuple

from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, substring_index, regexp_replace

from schema import Table, Catalog

class QueryGenerator():

    PERMISSIONS = {
        "readers": ["SELECT", "READ_METADATA", "USAGE"],
        "writers": ["SELECT", "READ_METADATA", "USAGE", "MODIFY", "CREATE"],
    }

    def __init__(self, spark: SparkSession, dbutils, debug: bool = False, no_grant: bool = False, no_comments: bool = False) -> None:
        self.queries = []
        self.debug = debug
        self.spark = spark
        self.dbutils = dbutils
        self.no_grant = no_grant
        self.comments = not no_comments
    
    def _create_table_query(self, table: Table) -> str:
        format = self.get_datatype(table.path)
        query = f"CREATE TABLE IF NOT EXISTS `{table.catalog}`.`{table.name}` USING {format} LOCATION '{table.path}';"
        comment = f"Creating table {table.catalog}.{table.name} with format {format} and path {table.path} if not exists"
        if self.debug: logging.info(query)
        return self._query_formatter(query, comment)

    def _create_catalog_query(self, catalog: Catalog) -> str:
        query = f"CREATE SCHEMA IF NOT EXISTS `{catalog.name}`;"
        comment = f"Creating catalog {catalog.name} if not exists"
        if self.debug: logging.info(query)
        return self._query_formatter(query, comment)

    def _create_schema_grant_query(self, catalog: str, permission: str, entity: str) -> str:
        query = f"GRANT {permission} ON SCHEMA `{catalog}` TO '{entity}';"
        comment = f"Adding {permission} permissions for {entity} on {catalog}"
        if self.debug: logging.info(query)
        return self._query_formatter(query, comment)
    
    def _create_table_grant_query(self, table: str, permission: str, entity: str) -> str:
        query = f"GRANT {permission} ON '{table}' TO '{entity}';"
        comment = f"Adding {permission} permissions for {entity} on table '{table}'"
        if self.debug: logging.info(query)
        return self._query_formatter(query, comment)

    def _query_formatter(self, query: str, comment: str) -> str:
        if self.comments:
            return f"-- {comment}\n{query}"
        else:
            return f"{query}"
        
    def _lookup_fs_tables(self, path: str) -> List[Tuple[str, str]]:
        if path == None: return []

        parsed = urlparse(path)
        schema = parsed.scheme

        if schema.lower() in ["abfss", "dbfs"]:
            if self.dbutils:
                files = [(fl.path, fl.name.split('/')[0]) for fl in self.dbutils.fs.ls(path) if fl.isDir()]
                return files
            else:
                if self.debug: logging.info("dbutils not found, skipping dbfs/abfss lookups")
                logging.warn("dbutils not found, skipping dbfs/abfss lookups")
                return []

        if schema.lower() == "file" or schema == "":
            # from parsed.path list all subdirectories
            # return a list of tuples
            if pathlib.Path(parsed.path).is_file():
                filename = parsed.path.split("/")[-1].split(".")[0]
                return [(path, filename)]
            else:
                opt = []
                for d in os.listdir(parsed.path):
                    opt.append((f"{path}/{d}", d))
                return opt
    
        if self.debug: logging.error(f"Schema {schema} is not supported")
        raise Exception(f"Schema {schema} is not supported")

    def get_datatype(self, path: str) -> str:
        if self.dbutils:
            if True in ["_delta_log" in f.path for f in self.dbutils.fs.ls(path)]: return "DELTA"
            if True in [str(f.path).endswith(".parquet") for f in self.dbutils.fs.ls(path)]: return "PARQUET"
            if True in [str(f.path).endswith(".csv") for f in self.dbutils.fs.ls(path)]: return "CSV"
            if True in [str(f.path).endswith(".json") for f in self.dbutils.fs.ls(path)]: return "JSON"
            if True in [str(f.path).endswith(".orc") for f in self.dbutils.fs.ls(path)]: return "ORC"
        else:
            p = path + "*" if path[-1] == "/" else path + "/*"
            files = self.spark.read.text(p)\
                .select(
                    input_file_name().alias('full_path'),
                    regexp_replace(input_file_name(), "^" + path + "/", "./").alias('relative_path'), 
                    substring_index(input_file_name(), "/", -1).alias('file_name'), 
                    substring_index(input_file_name(), ".", -1).alias('extension')
                )
            
            if files.filter(files.relative_path.contains("_delta_log")).count() >= 1:
                return "delta".upper()
            else:
                return str(files.groupBy("extension").count().first()[0]).upper()


    def get_queries(self) -> str:
        return "\n".join(self.queries)

    def clear_queries(self) -> None:
        self.queries = []

    def add_catalog(self, catalog: Catalog) -> None:
        lst = [d.name for d in self.spark.catalog.listDatabases()]
        if catalog.name not in lst:
            self.queries.append(self._create_catalog_query(catalog))

        tables = self._lookup_fs_tables(catalog.path)
        # TODO: in future rather than relying on sigle format in catalog allow for detection of format
        self.queries.extend([
            self._create_table_query(Table(name = table[1], path = table[0], catalog = catalog.name)) for table in tables
        ])

        if not self.no_grant:
            for role, entities in catalog.permissions.__dict__.items():
                try:
                    for grant in self.PERMISSIONS[role]:
                        self.queries.extend([
                            self._create_schema_grant_query(catalog.name, grant, entity) for entity in entities
                        ])
                except KeyError as e:
                    if self.debug: logging.warn(f"Role {role} is not supported, skipping role")
                    continue

    def add_table(self, table: Table) -> None:
        self.queries.append(self._create_table_query(table))

        if not self.no_grant:
            for role, entities in table.permissions.__dict__.items():
                try:
                    for grant in self.PERMISSIONS[role]:
                        self.queries.extend([
                            self._create_table_grant_query(f"{table.catalog}.{table.name}", grant, entity) for entity in entities
                        ])
                except KeyError as e:
                    if self.debug: logging.warn(f"Role {role} is not supported, skipping role")
                    continue
