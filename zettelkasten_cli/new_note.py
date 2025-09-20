import typer
import subprocess
import os
import re
from rich import print
from typing import Optional
from pathlib import Path
from zettelkasten_cli.utils import open_in_editor, load_config, parse_templater_commands

app = typer.Typer()


def create_new_note(
    title: Optional[str], template: Optional[str], vim_mode: bool
) -> None:
    """
    Create a new note from the command line.
    """
    cfg = load_config()
    try:
        note_title = get_note_title(
            prompt_title=cfg["file_settings"]["prompt_title"], title=title
        )
        validate_title(
            max_title_length=cfg["file_settings"]["max_title_length"], title=note_title
        )
        file_path = format_path(
            inbox_path=cfg["general"]["inbox_path"], title=note_title
        )
        create_file(
            general_cfg=cfg["general"],
            file_path=file_path,
            title=note_title,
            template=template,
        )
        if not vim_mode:
            open_in_editor(str(file_path))
    except ValueError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)
    except FileExistsError as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"An unexpected error occurred: {str(e)}", err=True)
        raise typer.Exit(code=1)


def get_note_title(prompt_title: str, title: Optional[str]) -> str:
    """
    Get the note title from input or prompt the user.
    """
    return title.strip() if title else typer.prompt(prompt_title)


def validate_title(max_title_length: int, title: str) -> None:
    """
    Validate the note title.
    """
    if not title:
        raise ValueError("Note title cannot be empty.")
    if len(title) > max_title_length:
        raise ValueError(f"Title cannot be more than {max_title_length} characters.")
    if title.endswith(".md"):
        raise ValueError("Leave out the .md extension.")


def format_path(inbox_path: str, title: str) -> Path:
    """
    Format the absolute path based on Zettelkasten location and the note title.
    """
    return f"{inbox_path}/{title}.md"


def create_file(
    general_cfg: dict[str, str], file_path: Path, title: str, template: Optional[str]
) -> None:
    """
    Create a new note file and open it in the editor.
    """
    if file_path.exists():
        raise FileExistsError(f"The file already exists: {file_path}")
    templated_text = apply_template(
        general_cfg=general_cfg, title=title, template=template
    )
    create_note_file(file_path=file_path, templated_text=templated_text)
    print(f"New note created: {file_path}")


def apply_template(
    template_cfg: dict[str, str], title: str, template: Optional[str]
) -> str:
    """
    Use a predefined template to create the new note. Parse any templater elements.
    """
    template_file = (
        template_cfg["default_template"] if not template else f"{template}.md"
    )
    template_path = f"{template_cfg['template_directory']}/{template_file}"
    templated_text = template_path.read_text()
    template = parse_templater_commands(templated_text=templated_text)
    return template


def create_note_file(file_path: Path, templated_text: str) -> None:
    """
    Create a new note file with the given title, append the title to the daily note, and add a H1 Markdown heading.
    """
    file_path.write_text(templated_text)
