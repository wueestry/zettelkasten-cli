import typer
import subprocess
import os
import re
from rich import print
from typing import Optional
from pathlib import Path
from zettelkasten_cli.config import (
    DEFAULT_TEMPLATE,
    DEFAULT_TEMPLATE_DIR,
    MAX_TITLE_LENGTH,
    INBOX_PATH,
    PROMPT_TITLE,
)
from zettelkasten_cli.utils import open_in_editor
from zettelkasten_cli.periodic_notes import append_daily_note

app = typer.Typer()


# TODO: Add H1 title to new note


def create_new_note(title, template, vim_mode) -> None:
    """Create a new note from the command line."""
    try:
        note_title = get_note_title(title)
        validate_title(note_title)
        file_path = format_path(note_title)
        create_file(file_path, note_title, template)
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


def get_note_title(title: Optional[str]) -> str:
    """Get the note title from input or prompt the user."""
    return title.strip() if title else typer.prompt(PROMPT_TITLE)


def validate_title(title: str) -> None:
    """Validate the note title."""
    if not title:
        raise ValueError("Note title cannot be empty.")
    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError(f"Title cannot be more than {MAX_TITLE_LENGTH} characters.")
    if title.endswith(".md"):
        raise ValueError("Leave out the .md extension.")


def format_path(note_title: str) -> Path:
    """Format the absolute path based on Zettelkasten location and the note title."""
    return INBOX_PATH / f"{note_title}.md"


def create_file(file_path: Path, note_title: str, template: Optional[str]) -> None:
    """Create a new note file and open it in the editor."""
    if file_path.exists():
        raise FileExistsError(f"The file already exists: {file_path}")
    templated_text = apply_template(note_title, template)
    create_note_file(file_path, templated_text)
    print(f"New note created: {file_path}")


def parse_commands(commands: list[str]) -> list[str]:
    for i in range(len(commands)):
        commands[i] = commands[i].replace("tp.file.", "")
        commands[i] = commands[i].replace("creation_date()", "formatDate(new Date())")
    return commands


def apply_template(note_title: str, template: Optional[str]) -> str:
    if not template:
        template_path = DEFAULT_TEMPLATE
    else:
        template_path = DEFAULT_TEMPLATE_DIR / template

    templated_text = template_path.read_text()

    commands = re.findall("(?<=<%).*(?=%>)", templated_text)

    commands = parse_commands(commands)

    js_command = f"""
    function formatDate(date) {{
        var d = new Date(date),
            day = ('0' + d.getDate()).slice(-2),
            month = ('0' + (d.getMonth() + 1)).slice(-2),
            year = d.getFullYear();
        return [year, month, day].join('-');
    }}

    var title = "{note_title}"
    """

    for i, line in enumerate(commands):
        js_command += f"var result{i} = {line}\n"
        js_command += f"console.log(result{i})\n"

    with open("template_evaluator.js", "w") as f:
        f.write(js_command)

    try:
        result = subprocess.check_output(
            ["node", "template_evaluator.js"], stderr=subprocess.STDOUT, text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.output}")

    os.remove("template_evaluator.js")

    results = result.split("\n")

    def replace_commands(match):
        return results.pop(0)

    templated_text = re.sub("(?=<%).*(?<=%>)", replace_commands, templated_text)

    return templated_text


def create_note_file(file_path: Path, templated_text: str) -> None:
    """
    Create a new note file with the given title, append the title to the daily note, and add a H1 Markdown heading.
    """
    file_path.write_text(templated_text)
