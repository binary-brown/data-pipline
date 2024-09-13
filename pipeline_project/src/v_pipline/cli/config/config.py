from json import load
from pathlib import Path
from typing import Any, List, Optional, Union

import typer
from pydantic import BaseModel
from rich.prompt import Prompt
from sqlalchemy import URL, Dialect, make_url
from yaml import safe_dump, safe_load


class Database(BaseModel):
	name: str
	host: Optional[str] = None
	port: Optional[int] = None
	dialect: Optional[type[Dialect]] = None
	driver: Optional[str] = None
	username: Optional[str] = None
	password: Optional[str] = None
	database: Optional[str] = None


class Provider(BaseModel):
	name: str
	provider_file_path: str

	def load(self) -> Any:
		if not Path(self.provider_file_path).is_file():
			raise FileNotFoundError(f"Provider file {self.provider_file_path} not found.")
		elif Path(self.provider_file_path).suffix == ".json":
			with open(self.provider_file_path, "r") as f:
				return load(f)
		else:
			with open(self.provider_file_path, "r") as f:
				return safe_load(f)


class VectorStore(BaseModel):
	name: str
	connection_string: str
	async_connection_string: str
	table_name: str
	schema_name: str


class Config(BaseModel):
	app_name: str = ""
	databases: List[Database] = []
	providers: List[Provider] = []
	vector_stores: List[VectorStore] = []

	def add_database_with_url(self, url: Union[str, URL]):
		url = make_url(url)
		database = Database(
			name=str(url.get_dialect()),
			host=url.host,
			port=url.port,
			dialect=url.get_dialect(),
			driver=url.drivername,
			username=url.username,
			password=url.password,
			database=url.database,
		)
		self.add_database(database)

	def add_database(self, database: Database):
		self.databases.append(database)

	def add_provider(self, provider: Provider):
		self.providers.append(provider)

	def add_vector_store(self, vector_store: VectorStore):
		self.vector_stores.append(vector_store)

	def get_provider(self, name: str) -> Any:
		provider = next((provider for provider in self.providers if provider.name == name), None)
		if not provider:
			raise ValueError(f"Provider {name} not found.")
		return provider.load()

	def get_vector_store(self, name: str):
		return next((vector_store for vector_store in self.vector_stores if vector_store.name == name), None)

	def get_database(self, name: str):
		return next((database for database in self.databases if database.name == name), None)

	def save(self):
		config_path = Path(self.config_dir) / "config.yaml"
		with open(config_path, "w") as f:
			safe_dump(self.model_dump(), f, sort_keys=True)
		return config_path

	@property
	def config_dir(self):
		return typer.get_app_dir(app_name=self.app_name)

	@staticmethod
	def new_config_in_dir(app_name: str, ask_user: bool = True):
		app_dir = typer.get_app_dir(app_name=app_name)
		config_path: Path = Path(app_dir) / "config.yaml"
		config = Config(app_name=app_name)
		if ask_user:
			create_config = Prompt.ask("Config file does not exist. Would you like to create one? [y/n]", default="y")
			if create_config.lower() != "y":
				return None
		if not Path(app_dir).is_dir():
			Path(app_dir).mkdir(parents=True, exist_ok=False)
		with open(config_path, "w") as f:
			safe_dump(config.model_dump(), f, sort_keys=False)
		return config

	@staticmethod
	def from_config_file(app_name: str, ask_user: bool = False):
		app_dir = typer.get_app_dir(app_name=app_name)
		config_path = Path(app_dir) / "config.yaml"
		config = None
		if not config_path.is_file():
			config = Config.new_config_in_dir(app_name, ask_user=ask_user)
		if not config:
			config = Config(app_name=app_name)
		with open(config_path, "r") as f:
			config_dict = safe_load(f)
			config = Config.model_validate(config_dict)
		return config
