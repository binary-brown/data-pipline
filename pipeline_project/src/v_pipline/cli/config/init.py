from pathlib import Path

import typer
from yaml import safe_dump

from .config import Config


def get_or_create_config(app_name: str):
	app_dir = typer.get_app_dir(app_name=app_name)
	config_path: Path = Path(app_dir) / "config.yaml"
	config = Config.from_config_file(app_name, ask_user=True)
	if config is None:
		return None
	with open(config_path, "w") as f:
		safe_dump(config.model_dump(), f)
