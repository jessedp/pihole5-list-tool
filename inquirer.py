""" prompts for inquirer """
import os
import sqlite3
from PyInquirer import prompt, Validator, ValidationError, Separator
import constants
import utils


def check_db(path):
    """ validate we have a good file """
    if not os.path.exists(path):
        utils.warn(" DOES NOT EXIST!")
        return False
    try:
        conn = sqlite3.connect(path)
    except (sqlite3.DatabaseError, sqlite3.OperationalError):
        utils.warn(" EXISTS, BUT IS NOT A SQLITE DATABASE!")
        return False

    try:
        sqldb = conn.cursor()
        _ = sqldb.execute("select count(*) from info")
        conn.close()
    except (sqlite3.DatabaseError, sqlite3.OperationalError):
        utils.warn(" IS NOT A PI-HOLE GRAVITY DB!")
        return False
    return True


class ValidateEditor(Validator):
    """Class to validator "editor" types since that's broken in current PyInquirer"""

    def validate(self, document):
        if document.text and len(document.text.split("\n")) <= 1:
            raise ValidationError(
                message="Must be at least 1 line", cursor_position=len(document.text)
            )


def key_prompt(questions):
    """ prompt wrapper to handle ctrl+c """
    resp = prompt(questions)
    if len(resp) != len(questions):
        raise KeyboardInterrupt
    return resp


def ask_db():
    """ prompt for gravity db file """
    questions = [
        {
            "name": "gravitydb",
            "type": "input",
            "default": constants.DEFAULT_DB,
            "message": "Gravity Db to Update:",
            "validate": lambda answer: "Please enter the full path to the │gravity.db│ (in your pi-hole configuration directory)."
            if not check_db(answer)
            else True,
        }
    ]
    result = key_prompt(questions)
    return result["gravitydb"]


def ask_list_type():
    """ prompt for white/black list """
    questions = [
        {
            "name": "listType",
            "type": "list",
            "default": "black",
            "message": "Add Blacklists or Whitelists?",
            "choices": [
                {
                    "name": "Blacklists",
                    "value": constants.BLACKLIST,
                    "short": "Blacklists",
                },
                {
                    "name": "Whitelists",
                    "value": constants.WHITELIST,
                    "short": "Whitelists",
                },
            ],
        }
    ]

    result = key_prompt(questions)
    return result["listType"]


def ask_blacklist():
    """ prompt for which blacklist to use """
    questions = [
        {
            "name": "source",
            "type": "list",
            "message": "Where are the block lists coming from?",
            "choices": [
                {
                    "name": """Firebog | Non-crossed lists : Use when someone is usually around to whitelist
             falsely blocked sites""",
                    "value": constants.B_FIREBOG_NOCROSS,
                    "short": "Firebog (no cross)",
                },
                {
                    "name": """Firebog | Ticked lists : Use where no one will be whitelisting falsely
             blocked sites""",
                    "value": constants.B_FIREBOG_TICKED,
                    "short": "Firebog (ticked)",
                },
                {
                    "name": """Firebog | All lists : Use when someone will always be around to
             whitelist falsely blocked sites""",
                    "value": constants.B_FIREBOG_ALL,
                    "short": "Firebog (all)",
                },
                Separator(),
                {
                    "name": "File    | A file with urls of lists, 1 per line",
                    "value": constants.FILE,
                    "short": "File",
                },
                {
                    "name": "Paste   | Paste urls of lists, 1 per line - opens editor, save, close",
                    "value": constants.PASTE,
                    "short": "Paste",
                },
            ],
        }
    ]

    result = key_prompt(questions)
    return result["source"]


def ask_whitelist():
    """ prompt for which blacklist to use """
    questions = [
        {
            "name": "source",
            "type": "list",
            "message": "Where are the whitelists coming from?",
            "choices": [
                {
                    "name": """AnudeepND | Whitelist Only :
        Domains that are safe to whitelist i.e does not contain any tracking or
        advertising sites. This fixes many problems like YouTube watch history,
        videos on news sites and so on.""",
                    "value": constants.W_ANUDEEP_WHITE,
                    "short": "AnudeepND (Whitelist)",
                },
                {
                    "name": """AnudeepND | Whitelist+Optional :
        These are needed depending on the service you use. They may contain some
        tracking sites but sometimes it's necessary to add bad domains to make a
        few services to work.""",
                    "value": constants.W_ANUDEEP_OPTIONAL,
                    "short": '"AndueepND (Whitelist+Optional)',
                },
                {
                    "name": """AnudeepND | Whitelist+Referral :
        People who use services like Slickdeals and Fatwallet need a few sites
        (most of them are either trackers or ads) to be whitelisted to work
        properly. This contains some analytics and ad serving sites like
        doubleclick.net and others. If you don't know what these services are,
        stay away from this list. Domains that are safe to whitelist i.e does
        not contain any tracking or advertising sites. This fixes many problems
        like YouTube watch history, videos on news sites and so on.""",
                    "value": constants.W_ANUDEEP_REFERRAL,
                    "short": "AndeepND (Whitelist+Referral)",
                },
                Separator(),
                {
                    "name": "File      | A file with urls of lists, 1 per line",
                    "value": constants.FILE,
                    "short": "File",
                },
                {
                    "name": "Paste     | Paste urls of lists, 1 per line - opens editor, save, close",
                    "value": constants.PASTE,
                    "short": "Paste",
                },
            ],
        }
    ]

    result = key_prompt(questions)
    return result["source"]


def ask_import_file():
    """ prompt for file to import from """
    questions = [
        {
            "name": "file",
            "type": "input",
            "message": "File to import",
            "validate": lambda value: "Please enter a valid file name."
            if not os.path.exists(value)
            else True,
        }
    ]
    result = key_prompt(questions)
    return result["file"]


def ask_paste():
    """ prompt for acquiring pasted list """
    questions = [
        {
            "name": "content",
            "type": "editor",
            "message": "Opening editor",
            # lambda text: len(text.split('\n')) >= 1 or 'Must be at least 1 line',
            "validate": ValidateEditor,
            "eargs": {"editor": "default", "ext": ".tmp"},
        }
    ]
    result = key_prompt(questions)
    return result["content"]


def confirm(message, default="y"):
    """ generic y/n confirm prompt """
    questions = [
        {
            "name": "confirm",
            "type": "confirm",
            "message": message,
            "default": default == "y",
        }
    ]
    result = key_prompt(questions)
    return result["confirm"]
