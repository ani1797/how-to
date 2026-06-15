import sys
from argparse import ArgumentParser
from random import randint

import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("dataset_file")
    parser.add_argument("output_dir")
    parser.add_argument("--test-size", type=float, default=0.3)
    return parser.parse_args(sys.argv)


def split(df: pd.DataFrame, test_size: float = 0.3, seed: int = randint(1, 10000)):
    # Split the DataFrame into training and testing sets
    train_df, test_df = train_test_split(df, test_size=test_size, random_state=seed)
    return train_df, test_df


if __name__ == "__main__":
    [dataset_file, output_dir, test_size] = sys.argv[1:]
    df = pd.read_csv(dataset_file)

    train_df, test_df = split(df, test_size=float(test_size) if test_size else 0.3)

    profile = {
        "train": {"rows": train_df.shape[0], "columns": train_df.shape[1]},
        "test": {"rows": test_df.shape[0], "columns": test_df.shape[1]},
    }
    mlflow.log_dict(profile, "data_profile.json")

    train_path = f"{output_dir}/iris_train.csv"
    test_path = f"{output_dir}/iris_test.csv"

    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    mlflow.log_artifact(train_path)
    mlflow.log_artifact(test_path)
