import typer
from pathlib import Path
from yaml import safe_load, safe_dump


def auth_with_google(app_name: str, client_secret_location: str):
    if client_secret_location != "" or client_secret_location is not None:
        app_dir = typer.get_app_dir(app_name=app_name)
        config_path = Path(app_dir) / "config.yaml"
        if not config_path.is_file():
            print("Please run the init command to create a config file.")
        else:
            with open(config_path, "r") as config_file:
                config = safe_load(config_file)
                config_yaml = safe_dump(
                    {"google": {"client_secret": client_secret_location}, **config}
                )
                with open(config_path, "w") as config_file:
                    config_file.writelines(config_yaml)


def auth_with_provider(app_name: str, provider: str):
    match provider:
        case "google":
            client_secret_location = typer.prompt(
                "Enter the location of the client secret file"
            )
            auth_with_google(app_name, client_secret_location)
        case _:
            print("Invalid provider")
