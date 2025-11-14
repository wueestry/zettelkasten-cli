import os
from pathlib import Path
from typing import Optional

import typer
import wget
from typing_extensions import Annotated

from zettelkasten_cli import new_note, periodic_notes

app = typer.Typer()


@app.command()
def new(
    title: Annotated[Optional[str], typer.Argument()] = None,
    template: Annotated[Optional[str], typer.Option("--template")] = None,
    vim_mode: Annotated[bool, typer.Option("--vim")] = True,
) -> None:
    """
    Create a new note with the provided title. Will prompt if no title given.
    Adds Obsidian markdown link to the daily note.
    """
    new_note.create_new_note(title=title, template=template, vim_mode=vim_mode)


@app.command()
def day() -> None:
    """
    Open daily note or create if it doesn't exist.
    """
    periodic_notes.open_daily_note()


@app.command()
def config(force: Annotated[bool, typer.Option("--force")] = False) -> None:
    """
    Creates a default config file in $XDG_CONFIG_HOME/zettelkasten-cli (default directory ~/.config/zettelkasten-cli)
    """
    if "XDG_CONFIG_HOME" in os.environ:
        config_path = os.path.join(os.environ["XDG_CONFIG_HOME"], "zettelkasten-cli")
    else:
        config_path = os.path.join(
            os.path.expanduser("~"), ".config", "zettelkasten-cli"
        )
    Path(config_path).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(os.path.join(config_path, "config.toml")) or force:
        example_config_url = "https://raw.githubusercontent.com/wueestry/zettelkasten-cli/refs/heads/main/example/config.toml"
        wget.download(example_config_url, out=config_path)
    else:
        raise Exception(
            "Config file is already present. Use --force to override the configuration file."
        )
