from pathlib import Path
from shutil import copyfile
from typing import Union

import typer
from rich import print
from rich.prompt import Prompt
from yaml import safe_dump

from v_pipline.cli.config.config import Config, Provider
from v_pipline.cli.config.provider_choices import ProviderChoice
from v_pipline.cli.decorators import log
from v_pipline.cli.exceptions.error_codes import VPErrorCodes


@log()
def check_for_dir(dir_path: Union[str, Path]):
	if not Path(dir_path).is_dir():
		make_dir = Prompt.ask("Credentials directory does not exist. Do you want to create it?", choices=["y", "n"], default="y")
		if make_dir == "y":
			Path(dir_path).mkdir(parents=True)
		else:
			typer.Exit(code=VPErrorCodes.USER_DECLINED)


@log()
def save_client_secret(app_dir: str, path_to_secret: str, provider_name: ProviderChoice):
	credentials_dir = Path(app_dir) / provider_name
	check_for_dir(credentials_dir)
	config_secret_file_path = Path(credentials_dir) / Path(path_to_secret).name
	copyfile(path_to_secret, config_secret_file_path)
	return config_secret_file_path


@log()
def get_credentials_file_location(app_dir: str, provider_name: ProviderChoice):
	client_secret_location = Prompt.ask("Enter the location of the client secret file")
	if not Path(client_secret_location).is_file():
		typer.Exit(code=VPErrorCodes.FILE_NOT_FOUND)
	elif client_secret_location != "" or client_secret_location is not None:
		client_secret_path = save_client_secret(app_dir, client_secret_location, provider_name)
		return client_secret_path
	else:
		typer.Exit(code=VPErrorCodes.INVALID_INPUT)


@log()
def auth_with_google(app_name: str):
	client_secret_location = Prompt.ask("Enter the location of the client secret file")
	if client_secret_location != "" or client_secret_location is not None:
		app_dir = typer.get_app_dir(app_name=app_name)
		config_path = Path(app_dir) / "config.yaml"
		if not Path(client_secret_location).is_file():
			typer.Exit(code=VPErrorCodes.FILE_NOT_FOUND)
		google_client_secret_path = save_client_secret(app_dir, client_secret_location, ProviderChoice.GOOGLE)
		if not config_path.is_file():
			print("Please run the init command to create a config file.")
			typer.Exit(code=VPErrorCodes.FILE_NOT_FOUND)
		else:
			config = Config.from_config_file(app_name)
			config.providers.append(Provider(name="google", provider_file_path=str(google_client_secret_path)))
			config.save()
	else:
		print("Client Secret Not Provided")
		typer.Exit(code=VPErrorCodes.INVALID_INPUT)


@log()
def auth_with_microsoft(app_name: str):
	tenent_id = Prompt.ask("Enter your Azure tenent id", password=False)
	client_id = Prompt.ask("Enter your Azure client id", password=False)
	client_secret = Prompt.ask("Enter your Azure client secret", password=True)
	resource_url = Prompt.ask("Enter your Azure resource url", password=False)
	if not all([client_id, client_secret, tenent_id, resource_url]):
		typer.Exit(code=VPErrorCodes.INVALID_INPUT)
	config = Config.from_config_file(app_name)
	config_dir = config.config_dir
	azure_config_dir = Path(config_dir) / "azure"
	check_for_dir(azure_config_dir)
	config_path = Path(azure_config_dir) / "credentials.yaml"
	with open(config_path, "w") as f:
		safe_dump({"client_id": client_id, "client_secret": client_secret, "tenent_id": tenent_id, "resource_url": resource_url}, f)
	config.add_provider(Provider(name="azure", provider_file_path=str(config_path)))
	config.save()


@log()
def auth_with_provider(app_name: str, provider: ProviderChoice):
	match provider:
		case ProviderChoice.GOOGLE:
			auth_with_google(app_name)
		case ProviderChoice.MICROSOFT:
			auth_with_microsoft(app_name)
		case _:
			print("Invalid provider")
