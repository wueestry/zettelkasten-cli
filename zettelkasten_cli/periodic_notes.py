from pathlib import Path

from zettelkasten_cli.new_note import create_new_note
from zettelkasten_cli.utils import (format_date, load_config,
                                    open_in_editor)

app = typer.Typer()


def open_daily_note() -> None:
    """
    Opens today's daily note in Neovim.
    Creates the note if it doesn't exist before opening.
    """

    cfg = load_config()
    today_note_path = Path(f"{cfg['general']['journal_directory']}{format_date()}.md")
    try:
        if not today_note_path.is_file():
            print(f"Creating new daily note: {today_note_path}")
            create_new_note(title=format_date(), template=cfg["general"]["daily_template"], vim_mode=True) 
        else:
            open_in_editor(cfg=cfg, file_path=today_note_path)
    except IOError as e:
        print(f"Error creating daily note: {e}")

