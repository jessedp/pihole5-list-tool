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


"""Makes bulk adding DNS blocklists and allowlists to Pi-hole 5 a breeze"""

import os
import sys
import sqlite3

import constants
import prompts
import allowlists
import blocklists
import utils
import banner


def main():
    """main method"""
    conn = None
    try:
        utils.clear()
        banner.display()

        use_docker = False
        docker = utils.find_docker()

        if docker[0] is True:
            utils.success(f"+ Found Running Docker config: {docker[1]}")
            use_docker = prompts.confirm("Use Docker-ized config?", "n")
            if use_docker:
                db_file = docker[1]

        if not use_docker:
            print()
            db_file = prompts.ask_db()

        # ask_db validates the db, pass this connection round for easy access & "global" mgmt
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        list_type = prompts.ask_list_type()

        print()
        utils.danger("    Do not hit ENTER or Y if a step seems to hang!")
        utils.danger("    Use CTRL+C if you're sure it's hung and report it.\n")

        if list_type == constants.BLOCKLIST:
            save = blocklists.manage_blocklists(cur)

        if list_type == constants.ALLOWLIST:
            save = allowlists.manage_allowlists(cur)

        if not save:
            conn.close()
            utils.warn("\nNothing changed. Bye!\n")
            sys.exit(0)

        conn.commit()
        conn.close()

        if prompts.confirm("Update Gravity for immediate effect?"):
            print()
            if use_docker:
                os.system('docker exec pihole bash "/usr/local/bin/pihole" "-g"')
            else:
                os.system("pihole -g")
        else:
            print()
            if use_docker:
                utils.info(
                    "Update Gravity through the web interface or by running:\n\t"
                    + '# docker exec pihole bash "/usr/local/bin/pihole" "-g"'
                )

            else:
                utils.info(
                    "Update Gravity through the web interface or by running:\n\t# pihole -g"
                )

            utils.info("\n\tBye!\n")

    except (KeyboardInterrupt, KeyError):
        if conn:
            conn.close()
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except sqlite3.OperationalError as err:
        utils.danger("\n\tDatabase error!")
        utils.danger(f"\t{err}")
    except (KeyboardInterrupt, KeyError):
        sys.exit(0)
