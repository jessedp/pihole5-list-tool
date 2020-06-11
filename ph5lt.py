#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2020 jessedp
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"),  to deal in the Software without restriction, including
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

__version__ = "0.4.8"


blackLists = {
    constants.B_FIREBOG_NOCROSS: {
        "url": "https://v.firebog.net/hosts/lists.php?type=nocross",
        "comment": "Firebog | Non-crossed lists",
    },
    constants.B_FIREBOG_ALL: {
        "url": "https://v.firebog.net/hosts/lists.php?type=all",
        "comment": "Firebog | All lists",
    },
    constants.B_FIREBOG_TICKED: {
        "url": "https://v.firebog.net/hosts/lists.php?type=tick",
        "comment": "Firebog | Ticked lists",
    },
}

ANUDEEP_WHITELIST = (
    "https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt"
)
whiteLists = {
    constants.W_ANUDEEP_WHITE: {
        "url": ANUDEEP_WHITELIST,
        "comment": "AndeepND | Whitelist Only",
    },
    constants.W_ANUDEEP_REFERRAL: {
        "url": "https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/referral-sites.txt",
        "comment": "AndeepND | Whitelist+Referral",
    },
    constants.W_ANUDEEP_OPTIONAL: {
        "url": "https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt",
        "comment": "AndeepND | Whitelist+Optional",
    },
}


def main():
    """main method"""
    try:
        utils.clear()
        print(color("    ┌──────────────────────────────────────────┐", fg="#b61042"))
        print(
            color("    │       ", fg="#b61042")
            + color(f"π-hole 5 list tool  v{__version__}", "#FFF")
            + color("         │", fg="#b61042")
        )
        print(color("    └──────────────────────────────────────────┘", fg="#b61042"))
        utils.info("    https://github.com/jessedp/pihole5-list-tool\n")

        db_file = ""
        use_docker = False
        docker = utils.find_docker()

        if docker[0] is True:
            utils.success(f"Found Running Docker config: {docker[1]}")
            use_docker = inquirer.confirm("Use Docker-ized config?", "n")
            if use_docker:
                db_file = docker[1]

        if not use_docker:
            db_file = inquirer.ask_db()

        list_type = inquirer.ask_list_type()

        print()
        utils.danger("    Do not hit ENTER or Y if a step seems to hang!")
        utils.danger("    Use CTRL+C if you're sure it's hung and report it.\n")

        if list_type == constants.BLACKLIST:
            process_blacklists(db_file)

        if list_type == constants.WHITELIST:
            process_whitelists(db_file)

        if inquirer.confirm("Update Gravity for immediate effect?"):
            print()
            if use_docker:
                os.system('docker exec pihole bash "/usr/local/bin/pihole" "-g"')
            else:
                os.system("pihole -g")
        else:
            if use_docker:
                utils.info(
                    "Update Gravity through the web interface or by running:\n\t"
                    + '# docker exec pihole bash "/usr/local/bin/pihole" "-g"'
                )

            else:
                utils.info(
                    "Update Gravity through the web interface or by running:\n\t# pihole -g"
                )

            utils.info("\n\tBye!")

    except (KeyboardInterrupt, KeyError):
        sys.exit(0)


def process_blacklists(db_file):
    """ prompt for and process blacklists """
    source = inquirer.ask_blacklist()

    import_list = []

    if source in blackLists:
        url_source = blackLists[source]
        resp = requests.get(url_source["url"])
        import_list = utils.process_lines(resp.text, url_source["comment"])

    if source == constants.FILE:
        fname = inquirer.ask_import_file()
        import_file = open(fname)
        import_list = utils.process_lines(import_file, f"File: {fname}")

    if source == constants.PASTE:
        import_list = inquirer.ask_paste()
        import_list = utils.process_lines(import_list, "Pasted content")

    if len(import_list) == 0:
        utils.die("No valid urls found, try again")

    if not inquirer.confirm(f"Add {len(import_list)} block lists to {db_file}?"):
        utils.warn("Nothing changed. Bye!")
        sys.exit(0)

    conn = sqlite3.connect(db_file)
    sqldb = conn.cursor()
    added = 0
    exists = 0
    for item in import_list:
        sqldb.execute("SELECT COUNT(*) FROM adlist WHERE address = ?", (item["url"],))

        cnt = sqldb.fetchone()

        if cnt[0] > 0:
            exists += 1
        else:
            added += 1
            vals = (item["url"], item["comment"])
            sqldb.execute(
                "INSERT OR IGNORE INTO adlist (address, comment) VALUES (?,?)", vals
            )
            conn.commit()

    sqldb.close()
    conn.close()

    utils.success(f"{added} block lists added! {exists} already existed.")


def process_whitelists(db_file):
    """ prompt for and process blacklists """
    source = inquirer.ask_whitelist()

    import_list = []

    if source in whiteLists:
        url_source = whiteLists[source]
        resp = requests.get(url_source["url"])
        import_list = utils.process_lines(resp.text, url_source["comment"], False)
        # This breaks if we add a new whitelist setup
        if source != ANUDEEP_WHITELIST:
            resp = requests.get(ANUDEEP_WHITELIST)
            import_list += utils.process_lines(resp.text, url_source["comment"], False)

    if source == constants.FILE:
        fname = inquirer.ask_import_file()
        import_file = open(fname)
        import_list = utils.process_lines(import_file.read(), f"File: {fname}", False)

    if source == constants.PASTE:
        import_list = inquirer.ask_paste()
        import_list = utils.process_lines(
            import_list, "Pasted content", utils.validate_host
        )

    if len(import_list) == 0:
        utils.die("No valid urls found, try again")

    if not inquirer.confirm(f"Add {len(import_list)} white lists to {db_file}?"):
        utils.warn("Nothing changed. Bye!")
        sys.exit(0)

    conn = sqlite3.connect(db_file)
    sqldb = conn.cursor()
    added = 0
    exists = 0

    for item in import_list:
        sqldb.execute(
            "SELECT COUNT(*) FROM domainlist WHERE domain = ?", (item["url"],)
        )

        cnt = sqldb.fetchone()

        if cnt[0] > 0:
            exists += 1
        else:
            # 0 = exact whitelist
            # 2 = regex whitelist
            domain_type = 0
            if item["type"] == constants.REGEX:
                domain_type = 2

            vals = (item["url"], domain_type, item["comment"])
            sqldb.execute(
                "INSERT OR IGNORE INTO domainlist (domain, type, comment) VALUES (?,?,?)",
                vals,
            )
            conn.commit()
            added += 1

    sqldb.close()
    conn.close()

    utils.success(f"{added} whitelists added! {exists} already existed.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, KeyError):
        sys.exit(0)
