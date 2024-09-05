# This is the main file for the CLI application. It is the entry point for the CLI application.
# Copyright (c) 2021 Christian J Brown
# License: MIT

import os
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich import print
from v_pipline.cli.config.authentication import auth_with_provider
from v_pipline.cli.config.init import get_or_create_config
from v_pipline.cli.utils.run_async import AsyncTyper
from v_pipline.cli.vectorize.file import ChunkType, vectorize_dir, vectorize_file

load_dotenv()

if os.getenv("DEBUG"):
    port = 5678
    host = "localhost"
    import debugpy

    debugpy.listen((host, port))
    print(f"Waiting for debugger to attach on {host}:{port}")
    debugpy.wait_for_client()


APP_NAME = "vp"

DEFAULT_CONFIG_SUFFIX = os.getenv("CONFIG_SUFFIX", ".yaml")

typer_app = AsyncTyper(name=APP_NAME, rich_markup_mode="rich")


@typer_app.async_command("auth")
async def auth(provider: str = typer.Argument("google")):
    """
    Authenticate with a provider:
    - [blue] Google
    - [blue] Github
    """
    auth_with_provider(APP_NAME, provider)


@typer_app.async_command()
async def init(
    database_url: Annotated[
        str, typer.Argument(envvar="DATABASE_URI", expose_value=False, hidden=True)
    ] = os.getenv("DATABASE_URI", None),
):
    """
    Initialize the application.
    This will create a configuration file.
    [bold green]DATABASE_URL[/bold green] is provided or [bold green]DATABASE_URI[/bold green] is set in the environment,
    it will be stored in the configuration file.
    """
    get_or_create_config(APP_NAME, database_url)


@typer_app.async_command()
async def vectorize(
    path_to_data: str = typer.Argument(...),
    chunk: bool = typer.Option(False),
    chunk_type: ChunkType = typer.Option(ChunkType.SENTENCE),
    chunk_size: int = typer.Option(None),
):
    """
    Vectorize a file or directory.
    """
    if os.path.isfile(path_to_data):
        print(f"Vectorizing file: {path_to_data}")
        await vectorize_file(path_to_data, chunk, chunk_type, chunk_size)
    elif os.path.isdir(path_to_data):
        print(f"Vectorizing directory: {path_to_data}")
        await vectorize_dir(path_to_data, chunk, chunk_type, chunk_size)


@typer_app.async_command()
async def main():
    print("Hello, World!")


if __name__ == "__main__":
    typer_app()
