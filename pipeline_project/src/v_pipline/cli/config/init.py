from pathlib import Path
from rich import print
import typer


def get_or_create_config(app_name: str, database_url: str = None):
    app_dir = typer.get_app_dir(app_name=app_name)
    config_path: Path = Path(app_dir) / "config.yaml"
    if not config_path.is_file():
        create_config = typer.prompt(
            "Config file does not exist. Would you like to create one? [y/n]"
        )
        if create_config.lower() == "y":
            if not Path(app_dir).is_dir():
                Path(app_dir).mkdir(parents=True, exist_ok=False)
            config_path.touch()
            print(f"Created config file at {config_path}")
    else:
        print(f"Config file already exists at {config_path}")
