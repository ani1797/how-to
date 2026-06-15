import os
import sys

import joblib
import mlflow
from ingest import ingest_iris_data
from split import split
from train import train
from transform import apply_transformations

# def normalized_env_name(environment: str) -> str:
#     supported_syms = {
#         "local": ["dev", "local", "development"],
#         "qa": ["test", "qa", "testing"],
#         "prod": ["prod", "production", "release", "main", "stable"],
#         "nonprod": ["nonprod", "non-prod", "nonproduction", "non-production"],
#     }
#     for k, v in supported_syms.items():
#         if environment.lower() in v:
#             return k


# def detect_environment():
#     env = os.getenv("ENV", "local")
#     return normalized_env_name(env)


# def get_config_files(env: str):
#     return os.listdir(f"config/{env}")


if __name__ == "__main__":
    mlflow.autolog()
    data_dir = sys.argv[1]

    # Ingest
    data = ingest_iris_data()
    data.to_csv(f"{data_dir}/iris.csv", index=False)
    mlflow.log_artifact(f"{data_dir}/iris.csv", artifact_path="raw")

    # Transform
    transformed_df = apply_transformations(data)
    data.to_csv(f"{data_dir}/iris_transformed.csv", index=False)
    mlflow.log_artifact(f"{data_dir}/iris.csv", artifact_path="gold")

    # Split
    train_df, test_df = split(transformed_df)
    train_df.to_csv(f"{data_dir}/iris_train.csv", index=False)
    test_df.to_csv(f"{data_dir}/iris_train.csv", index=False)

    # Log Data Profile
    profile = {
        "train": {"rows": train_df.shape[0], "columns": train_df.shape[1]},
        "test": {"rows": test_df.shape[0], "columns": test_df.shape[1]},
    }
    mlflow.log_dict(profile, "data_profile.json")

    # Train Model
    features = [
        "sepal_length_cm",
        "sepal_width_cm",
        "petal_length_cm",
        "petal_width_cm",
    ]
    target = ["target"]
    d_inputs = {
        "X_train": train_df[features],
        "X_test": test_df[features],
        "y_train": train_df[target],
        "y_test": test_df[target],
    }
    model = train(d_inputs["X_train"], d_inputs["y_train"])
    joblib.dump(model, f"{data_dir}/iris_svc.joblib")
