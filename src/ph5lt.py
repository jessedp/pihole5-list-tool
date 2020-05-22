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
import sys
from urllib.parse import urlparse
import sqlite3
import requests


from colors import color


import constants
import inquirer
import utils

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
        'comment': "AndeepND | Whitelist Only - Domains that are safe to whitelist i.e does not contain any tracking or advertising sites. This fixes many problems like YouTube watch history, videos on news sites and so on.",
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
    """main method"""
    try:
        print(color('\n    ┌──────────────────────────────────────────┐', fg='#b61042'))
        print(color('    │       ', fg='#b61042') +
              color(f'π-hole 5 list tool  v.{__version__}', '#FFF') + color('        │    ', fg='#b61042'))
        print(color('    └──────────────────────────────────────────┘\n', fg='#b61042'))

        result = inquirer.askDb()
        db_file = result['gravitydb']

        result = inquirer.askListType()
        list_type = result['listType']
        result = inquirer.askBlacklist()
        source = result['source']

        # Get imports from somewher
        import_list = []

        def valid_url(url):
            parts = urlparse(url.strip())
            return parts.scheme and parts.netloc

        def process_lines(data, comment):
            new_data = []
            for line in data.strip().split("\n"):
                line = line.strip()
                if line == '':
                    continue
                if not valid_url(line):
                    utils.warn(f'Skipping: {line}')
                else:
                    new_data.append({'url': line, 'comment': comment})
            return new_data

        if result['source'] in blackLists:
            url_source = blackLists[source]
            resp = requests.get(url_source['url'])
            import_list = process_lines(resp.text, url_source['comment'])

        if source == constants.FILE:
            choice = inquirer.askImportFile()
            fname = choice['file']

            import_file = open(fname)

            import_list = process_lines(import_file, f'File: {fname}')

        if source == constants.PASTE:
            choice = inquirer.askPaste()
            import_list = process_lines(choice['content'], 'Pasted content')

        if len(import_list) == 0:
            utils.die('No valid urls found, try again')

        choice = inquirer.confirm(
            f'Add {len(import_list)} block lists to {db_file}?')

        if not choice['confirm']:
            utils.warn('Nothing changed. Bye!')
            sys.exit(0)

        conn = sqlite3.connect(db_file)
        sqldb = conn.cursor()
        added = 0
        exists = 0
        for item in import_list:
            sqldb.execute(
                "SELECT COUNT(*) FROM adlist WHERE address = ?",
                (item['url'],))

            cnt = sqldb.fetchone()

            if cnt[0] > 0:
                exists += 1
            else:
                added += 1
                vals = (item['url'], item['comment'])
                sqldb.execute(
                    'INSERT OR IGNORE INTO adlist (address, comment) VALUES (?,?)', vals)
                conn.commit()

        sqldb.close()
        conn.close()

        utils.success(f'{added} block lists added! {exists} already existed.')

        choice = inquirer.confirm('Update Gravity for immediate affect?')

        if choice['confirm']:
            print()
            os.system('pihole -g')
        else:
            utils.info(
                'Update Gravity through the web interface or by running:\n\t# pihole -g')

            utils.info('\n\tBye!')

    except (KeyboardInterrupt, KeyError):
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, KeyError):
        sys.exit(0)
