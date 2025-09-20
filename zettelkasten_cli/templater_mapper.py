from datetime import datetime, timedelta


def date_formatter(n_day: int) -> str:
    return str(n_day) + (
        "th" if 4 <= n_day <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n_day % 10, "th")
    )


def templater_mapper(note_title: str, command: str) -> str:
    cmd = command.strip()  # Remove possible whitespaces

    if (
        cmd
        == '<% (tp.file.title.charAt(0).toUpperCase()+tp.file.title.slice(1)).split("-").join(" ") %>'
    ):
        templated_str = " ".join([t.capitalize() for t in note_title.splt("-")])
    elif cmd == '<% tp.file.title.split("-").join(" ").toUpperCase() %>':
        templated_str = " ".join([t.upper() for t in note_title.split("-")])
    elif cmd == "<% tp.file.creation_date() %>":
        templated_str = datetime.now().strftime("%Y-%m-%d")
    elif cmd == "<% tp.file.title %>":
        templated_str = note_title
    elif (
        cmd
        == "<% fileDate = moment(tp.file.title, 'YYYY-MM-DD').subtract(1, 'd').format('YYYY-MM-DD') %>]"
    ):
        templated_str = (datetime.now() - timedelta(1)).strftime("%Y-%m-%d")
    elif (
        cmd
        == "<% fileDate = moment(tp.file.title, 'YYYY-MM-DD').add(1, 'd').format('YYYY-MM-DD') %>]"
    ):
        templated_str = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")
    elif cmd == '<% tp.date.now("dddd, Do MMMM YYYY", 0, tp.file.title, "YYYYMMDD") %>':
        templated_str = (
            datetime.now()
            .strftime("%A, the {xx} %B %Y")
            .replace("{xx}", date_formatter(datetime.now().day()))
        )

    else:
        raise Exception(
            f"Command not found in current templater map. Please add the templating command {cmd} manually to the mapper."
        )

    return templated_str
