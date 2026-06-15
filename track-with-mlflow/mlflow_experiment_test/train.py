import os
import sys
from os import path

import joblib
import mlflow
import pandas as pd
from sklearn.svm import SVC


def train(X_train, y_train):
    model = SVC(kernel="rbf")
    model.fit(X_train, y_train)
    return model


if __name__ == "__main__":
    mlflow.autolog()

    [data_dir, output_dir] = sys.argv[1:]

    features = [
        "sepal_length_cm",
        "sepal_width_cm",
        "petal_length_cm",
        "petal_width_cm",
    ]
    target = ["target"]

    # loading training data
    train_df = pd.read_csv(f"{data_dir}/iris_train.csv")

    model = train(train_df[features], train_df[target])

    model_path = f"{output_dir}/iris_svc.joblib"
    os.makedirs(path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)

    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="mlflow-demo",
        registered_model_name="mlflow-demo",
    )
