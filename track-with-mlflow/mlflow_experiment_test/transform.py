import os
import sys
from os import path

import mlflow
import pandas as pd


def to_kebab_case(val: str) -> str:
    delimeter = "_"
    space = " "

    special_chars = ["/", "\\", "[", "]", "(", ")", "."]
    for char in special_chars:
        val = val.replace(char, "")

    words = val.split(space)

    kebab_case_val = delimeter.join(word.lower() for word in words)
    return kebab_case_val


def column_name_case(columns: list) -> dict:
    return {c: to_kebab_case(c) for c in columns}


def apply_transformations(df: pd.DataFrame) -> pd.DataFrame:
    columns = column_name_case(df.columns)
    df.rename(columns=columns, inplace=True)
    return df


if __name__ == "__main__":
    [dataset_file, output_dir] = sys.argv[1:]
    df = pd.read_csv(dataset_file)
    transformed_df = apply_transformations(df)
    transformed_path = f"{output_dir}/iris_transformed.csv"

    if not path.exists(path.dirname(transformed_path)):
        os.makedirs(path.dirname(transformed_path))

    transformed_df.to_csv(transformed_path, index=False)
    mlflow.log_artifact(transformed_path)
