import os
from pathlib import Path
import yaml

def load_config(config_path="config.yaml"):
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    # Validación básica
    required_sections = ["tools", "paths"]
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section in config: {section}")

    return config