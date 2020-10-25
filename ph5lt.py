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
import stats


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

        default = constants.BLOCKLIST
        option = ""
        any_save = False
        while option != constants.EXIT:
            stats.stat_bar(cur)
            option = prompts.main_menu(default)
            save = False

            if option == constants.BLOCKLIST:
                save = blocklists.manage_blocklists(cur)

            if option == constants.ALLOWLIST:
                save = allowlists.manage_allowlists(cur)

            if option == constants.STATS:
                stats.header(cur)

            if save:
                any_save = True
                default = constants.EXIT
                conn.commit()
                if option == constants.ALLOWLIST:
                    stats.allow_header(cur)

                if option == constants.BLOCKLIST:
                    stats.block_header(cur)

                if prompts.confirm("Are you finished?"):
                    break

        conn.close()
        if any_save:
            update_gravity(use_docker)

        utils.info("\n\tBye!\n")

    except (KeyboardInterrupt, KeyError):
        if conn:
            conn.close()
        sys.exit(0)


def update_gravity(use_docker):
    """ various ways of updating the gravity db """

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


if __name__ == "__main__":
    try:
        main()
    except sqlite3.OperationalError as err:
        utils.danger("\n\tDatabase error!")
        utils.danger(f"\t{err}")
    except (KeyboardInterrupt, KeyError):
        sys.exit(0)
