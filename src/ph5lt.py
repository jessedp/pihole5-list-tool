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
        'comment': "AndeepND | Whitelist Only - Domains that are safe to whitelist i.e does not contain any tracking or advertising sites. " +
                   "This fixes many problems like YouTube watch history, videos on news sites and so on.",
    },
    constants.W_ANUDEEP_REFERRAL: {
        'url': 'https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt',
        'comment': "AndeepND | Whitelist+Referral - People who use services like Slickdeals and Fatwallet need a few sites (most of them are " +
                   "either trackers or ads) to be whitelisted to work properly. This contains some analytics and ad serving sites like " +
                   "doubleclick.net and others. If you don't know what these services are, stay away from this list.	Domains that are safe " +
                   "to whitelist i.e does not contain any tracking or advertising sites. This fixes many problems like YouTube watch history, " +
                   "videos on news sites and so on.",
    },
    constants.W_ANUDEEP_OPTIONAL: {
        'url': 'https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt',
        'comment': "AndeepND | Whitelist+Optional - These are needed depending on the service you use. It may contain some tracking site but " +
                   "sometimes it's necessary to add bad domains to make a few services to work.",
    },
}


def main():
    """main method"""
    try:
        print(color('\n    ┌──────────────────────────────────────────┐', fg='#b61042'))
        print(color('    │       ', fg='#b61042') +
              color(f'π-hole 5 list tool  v.{__version__}', '#FFF') + color('        │    ', fg='#b61042'))
        print(color('    └──────────────────────────────────────────┘\n', fg='#b61042'))

        db_file = inquirer.ask_db()

        list_type = inquirer.ask_list_type()

        if list_type == constants.BLACKLIST:
            process_blacklists(db_file)

        if list_type == constants.WHITELIST:
            process_whitelists(db_file)

        if inquirer.confirm('Update Gravity for immediate affect?'):
            print()
            os.system('pihole -g')
        else:
            utils.info(
                'Update Gravity through the web interface or by running:\n\t# pihole -g')

            utils.info('\n\tBye!')

    except (KeyboardInterrupt, KeyError):
        sys.exit(0)


def process_blacklists(db_file):
    """ prompt for and process blacklists """
    source = inquirer.ask_blacklist()

    import_list = []

    if source in blackLists:
        url_source = blackLists[source]
        resp = requests.get(url_source['url'])
        import_list = utils.process_lines(resp.text, url_source['comment'])

    if source == constants.FILE:
        fname = inquirer.ask_import_file()
        import_file = open(fname)
        import_list = utils.process_lines(import_file, f'File: {fname}')

    if source == constants.PASTE:
        import_list = inquirer.ask_paste()
        import_list = utils.process_lines(import_list, 'Pasted content')

    if len(import_list) == 0:
        utils.die('No valid urls found, try again')

    if not inquirer.confirm(f'Add {len(import_list)} block lists to {db_file}?'):
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

    sqldb.close()
    conn.close()

    utils.success(f'{added} block lists added! {exists} already existed.')


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, KeyError):
        sys.exit(0)
