# Unity Catalog Helper

This project is made so that datascientists can manage and create the catalog with minimal effort and expand on the catalog with ease.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- pip

### Installing


2. Install the requirements
3. Run the script 

```bash

# 1. Clone the repository
git clone <repo> <folder>
cd <folder>

# 2. Install the requirements
pip install -r requirements.txt

# 3. Run the script
python unity_catalog_helper/create_catalog_sql.py # by default it will use the config file in the same directory as this readme.

# Optionally: access help and other options with the following command.
python unity_catalog_helper/create_catalog_sql.py --help
```


## Config file schema

```yaml
# This file serves as a static configuration for maintaining the catalog.
# The script will use this file to determine the location of the catalog and the location of the data along with permissions and other settings.

schemas:
    - name: name_of_schema
    path: path_to_data
    # Below properties are optional
    format: DELTA|PARQUET|CSV|JSON|ORC
    permissions:
        readers:
        # can be any number of group or user
        - some_user@some_domain.com
        - acl_group_name
        writers:
        # can be any number of group or user
        - some_user@some_domain.com
        - acl_group_name
    # Can also create an empty schema and not specify a path! just leave the path empty
    - name: name_of_schema
    path: ""
tables:
    - name: table_name
    catalog: specified_catalog_must_exist
    # Can be a single file or folder
    path: path_to_data
    # Below properties are optional
    format: DELTA|PARQUET|CSV|JSON|ORC
    permissions:
        readers:
        # can be any number of group or user
        - some_user@some_domain.com
        - acl_group_name
        writers:
        # can be any number of group or user
        - some_user@some_domain.com
        - acl_group_name
    # Can also create just a table without any permissions or specifying format (delta is default)
    - name: table_name
    catalog: specified_catalog_must_exist
    path: path_to_data
```
