import subprocess
import os
import tomllib
import re
from datetime import datetime, timedelta

from pathlib import Path
from typing import Union

from rich import print

from zettelkasten_cli.templater_mapper import templater_mapper


def format_date(delta_days=0):
    """
    Returns a specified day as a string
    """
    return (datetime.now() + timedelta(days=delta_days)).strftime("%Y-%m-%d")


def format_week(delta_days=0):
    """
    Returns the week of a specified day in a string format
    """
    return (
        datetime.now() + timedelta(days=delta_days - datetime.now().weekday())
    ).strftime("%Y-W%V")


def load_config() -> dict[str, dict[str, str]]:
    """
    Load the configuration file and save all configs in a dict.
    """
    config_path = os.path.join(
        os.environ["XDG_CONFIG_HOME"], "zettelkasten-cli", "config.toml"
    )
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
    except Exception:
        raise Exception(
            "Config not found. Run zk config first to generate a configuration file."
        )

    for category, data in config.items():
        for key, value in data.items():
            if isinstance(value, str) and "~" in value:
                config[category][key] = os.path.expanduser(value)
    return config


def open_in_editor(cfg: dict[str, dict[str, str]], file_path: Union[str, Path]) -> None:
    """
    Open the file in the configured editor.
    """
    # Convert Path objects to strings if needed
    if isinstance(file_path, Path):
        file_path = str(file_path)

    try:
        if cfg["general"]["editor"] == "nvim":
            cmd = ["nvim", cfg["neovim"]["arguments"], file_path]

            # Add any additional commands
            for nvim_cmd in cfg["neovim"]["commands"]:
                if nvim_cmd and nvim_cmd.strip():  # only add non-empty commands
                    cmd.extend(["-c", nvim_cmd.strip()])
        else:
            # For other editors, just use the basic command
            cmd = [cfg["general"]["editor"], file_path]

        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to open the file with {cfg['general']['editor']}: {e}")
    except FileNotFoundError:
        print(
            f"Error: {cfg['general']['editor']} command not found. Make sure it's installed and in your PATH."
        )


def parse_templater_commands(note_title: str, templated_text: str):
    """
    Parse a template by mapping javascript snippets to the correct python snippets.
    """
    commands = re.findall("(?<=<%).+?(?=%>)", templated_text)

    replaced_templates = []
    for i in range(len(commands)):
        replaced_templates.append(
            templater_mapper(note_title=note_title, command=commands[i])
        )

    def replace_commands(match):
        return replaced_templates.pop(0)

    template = re.sub("(?=<%).+?(?<=%>)", replace_commands, templated_text)

    return template
