import os
from pathlib import Path

# Paths
ZETTELKASTEN_ROOT = Path(os.environ.get("ZETTELKASTEN", ""))
INBOX_PATH = ZETTELKASTEN_ROOT / "inbox"

# File settings
MAX_TITLE_LENGTH = 80

# Prompts
PROMPT_TITLE = "Enter the title of the note"

# Commands
EDITOR_COMMAND = "nvim"

# Only use default arguments if environment variable is not set
NVIM_ARGS = os.environ.get("ZETTELKASTEN_NVIM_ARGS") or "+ normal Gzzo"

# Only use default commands if environment variable is not set
nvim_cmds = os.environ.get("ZETTELKASTEN_NVIM_COMMANDS")
NVIM_COMMANDS = nvim_cmds.split(",") if nvim_cmds else [""]

DEFAULT_TEMPLATE_DIR = ZETTELKASTEN_ROOT / "meta" / "templates"
DEFAULT_TEMPLATE = DEFAULT_TEMPLATE_DIR / "note-template.md"
