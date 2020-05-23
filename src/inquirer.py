""" prompts for inquirer """
import os
from PyInquirer import prompt, Validator, ValidationError
import constants


class ValidateEditor(Validator):
    """Class to validator "editor" types since that's broken in current PyInquirer"""

    def validate(self, document):
        if document.text and len(document.text.split('\n')) <= 1:
            raise ValidationError(
                message='Must be at least 1 line',
                cursor_position=len(document.text)
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
            'name': 'gravitydb',
            'type': 'input',
            'default': constants.DEFAULT_DB,
            'message': 'Gravity Db to Update:',
            'validate':
                lambda answer: f'Please enter a valid file name or nothing for {constants.DEFAULT_DB} {answer}.'
            if answer.strip() != '' and not os.path.exists(answer) else True

        }
    ]
    result = key_prompt(questions)
    return result['gravitydb']


def ask_list_type():
    """ prompt for white/black list """
    questions = [
        {
            'name': 'listType',
            'type': 'list',
            'default': 'black',
            'message': 'Add Blacklists or Whitelist?',
            'choices': [
                {
                    'name':
                    'Blacklists',
                    'value': constants.BLACKLIST,
                    'short': 'Blacklists',
                },
                {
                    'name':
                    'Whitelists',
                    'value': constants.WHITELIST,
                    'short': 'Whitelists',
                },
            ],

        }
    ]

    result = key_prompt(questions)
    return result['listType']


def ask_blacklist():
    """ prompt for which blacklist to use """
    questions = [
        {
            'name': 'source',
            'type': 'list',
            'message': 'Where are the block lists coming from?',
            'choices': [
                {
                    'name':
                    'Firebog | Non-crossed lists: For when someone is usually around to whitelist falsely blocked sites',
                    'value': constants.B_FIREBOG_NOCROSS,
                    'short': 'Firebog (no cross)',
                },
                {
                    'name':
                    'Firebog | Ticked lists: For when installing Pi-hole where no one will be whitelisting falsely blocked sites',
                    'value': constants.B_FIREBOG_TICKED,
                    'short': 'Firebog (ticked)',
                },
                {
                    'name': 'Firebog | All lists: For those who will always be around to whitelist falsely blocked sites',
                    'value': constants.B_FIREBOG_ALL,
                    'short': 'Firebog (all)',
                },
                {
                    'name': 'File    | A file with urls of lists, 1 per line',
                    'value': constants.FILE,
                    'short': 'File',
                },
                {
                    'name': 'Paste   | Paste urls of lists, 1 per line - opens editor, save, close',
                    'value': constants.PASTE,
                    'short': 'Paste',
                },
            ]
        }
    ]

    result = key_prompt(questions)
    return result['source']


def ask_import_file():
    """ prompt for file to import from """
    questions = [
        {
            'name': 'file',
            'type': 'input',
            'message': 'File to import',
            'validate': lambda value: 'Please enter a valid file name.' if not os.path.exists(value) else True
        }
    ]
    result = key_prompt(questions)
    return result['file']


def ask_paste():
    """ prompt for acquiring pasted list """
    questions = [
        {
            'name': 'content',
            'type': 'editor',
            'message': 'Opening editor',
            # lambda text: len(text.split('\n')) >= 1 or 'Must be at least 1 line',
            'validate': ValidateEditor,
            'eargs': {
                'editor': 'default',
                'ext': '.tmp'
            },

        }
    ]
    result = key_prompt(questions)
    return result['content']


def confirm(message):
    """ generic y/n confirm prompt """
    questions = [
        {
            'name': 'confirm',
            'type': 'confirm',
            'message': message,
            'default': 'y',
        }
    ]
    result = key_prompt(questions)
    return result['confirm']
