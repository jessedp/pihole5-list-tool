#!/usr/bin/env python
"""lastseen-cli is a client to update your lastseen time on lastseen.me"""
import os
from sys import exit
from urllib.parse import urlparse
import requests
import sqlite3

from colors import color, strip_color
from pprint import pprint

import inquirer
import constants


a = "1"
urlLists = {

    constants.FIREBOG_NOCROSS: {
        'url': 'https://v.firebog.net/hosts/lists.php?type=nocross',
        'comment': f'Firebog {a}| Non-crossed lists',
    },
    constants.FIREBOG_ALL: {
        'url': 'https://v.firebog.net/hosts/lists.php?type=all',
        'comment': 'Firebog | All lists',
    },
    constants.FIREBOG_TICKED: {
        'url': 'https://v.firebog.net/hosts/lists.php?type=tick',
        'comment': 'Firebog | Ticked lists',
    }
}


def main():
    print(color("""
    +--------------------------------------+
    |       pihole 5 list tool             |
    +--------------------------------------+
""", fg='lime'))

    config = inquirer.askSetup()
    source = config['source']
    dbFile = config['gravitydb']

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

    if config['source'] in urlLists:
        urlSource = urlLists[source]
        resp = requests.get(urlSource['url'])
        importList = processLines(resp.text, urlSource['comment'])

    if source == constants.FILE:
        choice = inquirer.askImportFile()
        file = choice['file']
        f = open(file)
        importList = processLines(f.read(), f'File: {file}')

    if source == constants.PASTE:
        choice = inquirer.askPaste()
        importList = processLines(choice['content'], 'Pasted content')

    if len(importList) == 0:
        die('No valid urls found, try again')

    choice = inquirer.confirm(f'Add {len(importList)} block lists to {dbFile}?')

    if choice['confirm'] is True:
        warn('Nothing changed. Bye!')
        exit(0)

    conn = sqlite3.connect(config['gravitydb'])
    db = conn.cursor()
    added = 0
    exists = 0
    for item in importList:
        db.execute(
            "SELECT COUNT(*) FROM adlist WHERE address = ?", (item['url'],) )

        cnt = db.fetchone()

        if cnt[0] > 0:
            exists += 1
        else:
            added += 1
            db.execute(
                'INSERT OR IGNORE INTO adlist (address, comment) VALUES (?,?)',
                item['url'], item['comment'])
            conn.commit()

    db.close()
    conn.close()

    success(f'{added} block lists added! {exists} already existed.')

    choice = inquirer.confirm('Update Gravity for immediate affect?')
    if choice['confirm'] == 'y':
        print()
        os.system('pihole -g')
    else:
        info('Update Gravity through the web interface or by running:\n\t# pihole -g')

    info('\n\tBye!')


def warn(msg):
    print(color(msg, fg='yellow'))


def success(msg):
    print(color(msg, fg='lime'))


def info(msg):
    print(color(msg, fg='#5DADE2'))


def die(msg):
    print(color(msg, fg='orangered'))
    exit(-1)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, KeyError):
        exit(0)