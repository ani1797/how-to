import sys

import mlflow
import pandas as pd
import sklearn as sk


def ingest_iris_data() -> pd.DataFrame:
    # Note: Since I'll just be using iris dataset, I will just pull the data from sklearn.
    # Other sources can be used as well and parameterized to fetch portions of data as needed.
    frame = sk.datasets.load_iris(as_frame=True)
    df = pd.DataFrame(data=frame.data, columns=frame.feature_names)
    df["target"] = frame.target
    return df


if __name__ == "__main__":
    mlflow.autolog()
    data = ingest_iris_data()
    [output_dir] = sys.argv[1:]
    if not output_dir:
        print("No output directory specified. Exiting...")
        sys.exit(1)
    data.to_csv(f"{output_dir}/iris.csv", index=False)
    mlflow.log_artifact(f"{output_dir}/iris.csv")
