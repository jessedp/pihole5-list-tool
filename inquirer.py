from os import path
from colors import color
from PyInquirer import prompt, Validator, ValidationError

import constants

defaultDb = '/etc/pihole/gravity.db'


class ValidateEditor(Validator):
    def validate(self, document):
        if document.text and len(document.text.split('\n')) <= 1:
            raise ValidationError(
                message='Must be at least 1 line', cursor_position=len(document.text))


def keyPrompt(questions):
    resp = prompt(questions)
    if len(resp) != len(questions):
        raise KeyboardInterrupt
    return resp


def askSetup():
    questions = [
        {
            'name': 'gravitydb',
                    'type': 'input',
                    'default': defaultDb,
                    'message': 'Gravity Db to Update:',
                    'validate': lambda answer: f'Please enter a valid file name or nothing for {defaultDb} {answer}.'
            if answer.strip() != '' and not path.exists(answer) else True

        },
        {
            'name': 'source',
                    'type': 'list',
                    'message': 'Where are the block lists coming from?',
                    'choices': [
                        {
                            'name':
                            'Firebog | Non-crossed lists: For when someone is usually around to whitelist falsely blocked sites',
                            'value': constants.FIREBOG_NOCROSS,
                            'short': 'Firebog (no cross)',
                        },
                        {
                            'name':
                            'Firebog | Ticked lists: For when installing Pi-hole where no one will be whitelisting falsely blocked sites',
                            'value': constants.FIREBOG_TICKED,
                            'short': 'Firebog (ticked)',
                        },
                        {
                            'name': 'Firebog | All lists: For those who will always be around to whitelist falsely blocked sites',
                            'value': constants.FIREBOG_ALL,
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
                    ],
        },
    ]

    return keyPrompt(questions)


def askImportFile():
    questions = [
        {
            'name': 'file',
            'type': 'input',
            'message': 'File to import',
            'validate': lambda value: 'Please enter a valid file name.' if not path.exists(value) else True
        },
    ]

    return keyPrompt(questions)


def askPaste():
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


        },
    ]
    return keyPrompt(questions)


def confirm(message):
    questions = [
        {
            'name': 'confirm',
            'type': 'confirm',
            'message': message,
            'default': 'y',
        },
    ]
    return keyPrompt(questions)
