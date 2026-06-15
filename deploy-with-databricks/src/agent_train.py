from logging import getLogger

import mlflow
import mlflow.langchain
from langchain_openai import AzureChatOpenAI

from databricks_asset_bundle.large_language_model.lg_agent import create_agent

llm = AzureChatOpenAI(model="gpt-4.1")
graph = create_agent(llm)
mlflow.models.set_model(graph)


def parse_args(argv):
    import argparse

    parser = argparse.ArgumentParser(description="Train a general-purpose agent.")
    parser.add_argument(
        "--model_name",
        type=str,
        help="The model to use for registration.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    import sys

    args = parse_args(sys.argv[1:])
    log = getLogger(__name__)

    with mlflow.start_run() as run:
        log.info("Active run ID: %s", run.info.run_id)
        model_info = mlflow.langchain.log_model(
            lc_model="./agent_train.py",
            artifact_path="model",
            code_paths=[
                "./databricks_asset_bundle",
            ],
        )
        log.info("Model URI: %s", model_info.model_uri)
        mlflow.register_model(
            model_uri=model_info.model_uri,
            name=args.model_name,
            tags={"model_type": "general_purpose"},
        )
