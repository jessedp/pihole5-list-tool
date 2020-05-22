#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2020 jessedp
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""Makes bulk adding DNS blacklists and whitelists to Pi-hole 5 a breaaze"""


import os
from sys import exit
from urllib.parse import urlparse
import requests
import sqlite3


from colors import color
from PyInquirer import prompt, Validator, ValidationError

import constants

# from pprint import pprint


__version__ = '0.3.3'


blackLists = {
    constants.B_FIREBOG_NOCROSS: {
        'url': 'https://v.firebog.net/hosts/lists.php?type=nocross',
        'comment': 'Firebog | Non-crossed lists',
    },
    constants.B_FIREBOG_ALL: {
        'url': 'https://v.firebog.net/hosts/lists.php?type=all',
        'comment': 'Firebog | All lists',
    },
    constants.B_FIREBOG_TICKED: {
        'url': 'https://v.firebog.net/hosts/lists.php?type=tick',
        'comment': 'Firebog | Ticked lists',
    }
}

whiteLists = {
    constants.W_ANUDEEP_WHITE: {
        'url': 'https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt',
        'comment': 'AndeepND | Whitelist Only - Domains that are safe to whitelist i.e does not contain any tracking or advertising sites. This fixes many problems like YouTube watch history, videos on news sites and so on.',
    },
    constants.W_ANUDEEP_REFERRAL: {
        'url': 'https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt',
        'comment': "AndeepND | Whitelist+Referral - People who use services like Slickdeals and Fatwallet need a few sites (most of them are either trackers or ads) to be whitelisted to work properly. This contains some analytics and ad serving sites like doubleclick.net and others. If you don't know what these services are, stay away from this list.	Domains that are safe to whitelist i.e does not contain any tracking or advertising sites. This fixes many problems like YouTube watch history, videos on news sites and so on.",
    },
    constants.W_ANUDEEP_OPTIONAL: {
        'url': 'https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt',
        'comment': "AndeepND | Whitelist+Optional - These are needed depending on the service you use. It may contain some tracking site but sometimes it's necessary to add bad domains to make a few services to work.",
    },
}


def main():
    try:
        print(color('\n    ┌──────────────────────────────────────────┐', fg='#b61042'))
        print(color('    │       ', fg='#b61042') +
              color(f'π-hole 5 list tool  v.{__version__}', '#FFF') + color('        │    ', fg='#b61042'))
        print(color('    └──────────────────────────────────────────┘\n', fg='#b61042'))

        result = askDb()
        dbFile = result['gravitydb']

        result = askListType()
        type = result['listType']
        result = askBlacklist()
        source = result['source']

        # Get imports from somewher
        importList = []

        def validUrl(url):
            parts = urlparse(url.strip())
            return parts.scheme and parts.netloc

        def processLines(data, comment):
            newData = []
            for line in data.strip().split("\n"):
                line = line.strip()
                if line == '':
                    continue
                if not validUrl(line):
                    warn(f'Skipping: {line}')
                else:
                    newData.append({'url': line, 'comment': comment})
            return newData

        if config['source'] in blackLists:
            urlSource = blackLists[source]
            resp = requests.get(urlSource['url'])
            importList = processLines(resp.text, urlSource['comment'])

        if source == FILE:
            choice = askImportFile()
            file = choice['file']
            f = open(file)
            importList = processLines(f.read(), f'File: {file}')

        if source == PASTE:
            choice = askPaste()
            importList = processLines(choice['content'], 'Pasted content')

        if len(importList) == 0:
            die('No valid urls found, try again')

        choice = confirm(
            f'Add {len(importList)} block lists to {dbFile}?')

        if not choice['confirm']:
            warn('Nothing changed. Bye!')
            exit(0)

        conn = sqlite3.connect(config['gravitydb'])
        db = conn.cursor()
        added = 0
        exists = 0
        for item in importList:
            db.execute(
                "SELECT COUNT(*) FROM adlist WHERE address = ?", (item['url'],))

            cnt = db.fetchone()

            if cnt[0] > 0:
                exists += 1
            else:
                added += 1
                vals = (item['url'], item['comment'])
                db.execute(
                    'INSERT OR IGNORE INTO adlist (address, comment) VALUES (?,?)', vals)
                conn.commit()

        db.close()
        conn.close()

        success(f'{added} block lists added! {exists} already existed.')

        choice = confirm('Update Gravity for immediate affect?')

        if choice['confirm']:
            print()
            os.system('pihole -g')
        else:
            info('Update Gravity through the web interface or by running:\n\t# pihole -g')

            info('\n\tBye!')

    except (KeyboardInterrupt, KeyError):
        exit(0)


def warn(msg):
    print(color(msg, fg='yellow'))


def success(msg):
    print(color(msg, fg='lime'))


def info(msg):
    print(color(msg, fg='#5DADE2'))


def die(msg):
    print(color(msg, fg='orangered'))
    exit(-1)


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


def askDb():
    questions = [
        {
            'name': 'gravitydb',
                    'type': 'input',
                    'default': constants.defaultDb,
                    'message': 'Gravity Db to Update:',
                    'validate': lambda answer: f'Please enter a valid file name or nothing for {defaultDb} {answer}.'
            if answer.strip() != '' and not os.path.exists(answer) else True

        }
    ]

    return keyPrompt(questions)


def askListType():
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

    return keyPrompt(questions)


def askBlacklist():
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

    return keyPrompt(questions)


def askImportFile():
    questions = [
        {
            'name': 'file',
            'type': 'input',
            'message': 'File to import',
            'validate': lambda value: 'Please enter a valid file name.' if not os.path.exists(value) else True
        }
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

        }
    ]
    return keyPrompt(questions)


def confirm(message):
    questions = [
        {
            'name': 'confirm',
            'type': 'confirm',
            'message': message,
            'default': 'y',
        }
    ]
    return keyPrompt(questions)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, KeyError):
        exit(0)
