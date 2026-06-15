import os


def normalized_env_name(environment: str) -> str:
    supported_syms = {
        "local": ["dev", "local", "development"],
        "qa": ["test", "qa", "testing"],
        "prod": ["prod", "production", "release", "main", "stable"],
        "nonprod": ["nonprod", "non-prod", "nonproduction", "non-production"],
    }
    for k, v in supported_syms.items():
        if environment.lower() in v:
            return k


def detect_environment():
    env = os.getenv("ENV", "local")
    return normalized_env_name(env)


def read_config(filepath: str):
    _, ext = os.path.splitext(filepath)
    if ext == ".yaml":
        import yaml

        with open(filepath) as f:
            return yaml.safe_load(f)
    elif ext == ".json":
        import json

        with open(filepath) as f:
            return json.load(f)
    else:
        raise ValueError(f"Invalid config file extension: {ext}")


def merge_dict(dict1: dict, dict2: dict) -> dict:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def get_config(env: str):
    env = normalized_env_name(env)
    config_file = [f"config/{env}/config.yaml", f"config/{env}/config.json"]
    effective_config = {}
    for file in config_file:
        if os.path.exists(file):
            cfg = read_config(file)
            effective_config = merge_dict(effective_config, cfg)
    return effective_config


def current_config():
    env = detect_environment()
    return get_config(env)
