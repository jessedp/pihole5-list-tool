""" add/remove/reset blocklists """
import requests
from PyInquirer import Separator

import prompts
import constants
import utils

ANUDEEP_ALLOWLIST = (
    "https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/whitelist.txt"
)
whiteLists = {
    constants.W_ANUDEEP_ALLOW: {
        "url": ANUDEEP_ALLOWLIST,
        "comment": "AnudeepND | Allowlist Only",
    },
    constants.W_ANUDEEP_REFERRAL: {
        "url": "https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/referral-sites.txt",
        "comment": "AnudeepND | Allowlist+Referral",
    },
    constants.W_ANUDEEP_OPTIONAL: {
        "url": "https://raw.githubusercontent.com/anudeepND/whitelist/master/domains/optional-list.txt",
        "comment": "AnudeepND | Allowlist+Optional",
    },
}


def manage_allowlists(cur):
    """ what to do to allowlists """
    questions = [
        {
            "name": "action",
            "type": "list",
            "default": "add",
            "message": "Allowlist action:",
            "choices": [
                {"name": "Add a list", "value": "add",},
                Separator(),
                {"name": "Remove Lists Added by This Tool", "value": "remove",},
                {"name": "Remove ALL Allowlists", "value": "empty",},
            ],
        }
    ]

    result = prompts.key_prompt(questions)
    action = result["action"]
    if action == "add":
        return add(cur)

    if action == "empty":
        return empty(cur)

    if action == "remove":
        return remove(cur)

    return False


def add(cur):
    """ prompt for and process allowlists """
    source = prompts.ask_allowlist()

    utils.warn_long_running()

    import_list = []

    if source in whiteLists:
        url_source = whiteLists[source]
        resp = requests.get(url_source["url"])
        import_list = utils.process_lines(resp.text, url_source["comment"], False)
        # This breaks if we add a new whitelist setup
        if source != ANUDEEP_ALLOWLIST:
            resp = requests.get(ANUDEEP_ALLOWLIST)
            import_list += utils.process_lines(resp.text, url_source["comment"], False)

    if source == constants.FILE:
        fname = prompts.ask_import_file()
        import_file = open(fname)
        import_list = utils.process_lines(import_file.read(), f"File: {fname}", False)

    if source == constants.PASTE:
        import_list = prompts.ask_paste()
        import_list = utils.process_lines(
            import_list, "Pasted content", utils.validate_host
        )

    if len(import_list) == 0:
        utils.die("No valid urls found, try again")

    if not prompts.confirm(f"Add {len(import_list)} white lists?"):
        return False

    added = 0
    exists = 0

    for item in import_list:
        cur.execute("SELECT COUNT(*) FROM domainlist WHERE domain = ?", (item["url"],))

        cnt = cur.fetchone()

        if cnt[0] > 0:
            exists += 1
        else:
            # 0 = exact whitelist
            # 2 = regex whitelist
            domain_type = 0
            if item["type"] == constants.REGEX:
                domain_type = 2

            vals = (item["url"], domain_type, item["comment"] + " [ph5lt]")
            cur.execute(
                "INSERT OR IGNORE INTO domainlist (domain, type, comment) VALUES (?,?,?)",
                vals,
            )
            added += 1
    utils.success(f"{added} allowlists added! {exists} already existed.")
    return True


def empty(cur):
    """ remove all block lists"""
    utils.danger(
        """
    This will REMOVE ALL manually added allowlists!
    You probably DO NOT want to do this!
"""
    )

    if prompts.confirm("Are you sure?", "n"):
        cur.execute("DELETE FROM domainlist WHERE type in (0,2)")
        return True

    return False


##### Deal with my sloppiness...
def remove(cur):
    """ remove lists we added """

    utils.info(
        """
    This will try to remove blocklists added by this tool. Removal is done
    based on the comment for each list. If you've never changed any comments
    or used other tools, this is 100% safe.
"""
    )

    if prompts.confirm("Are you sure?", "n"):
        cur.execute(
            "DELETE FROM domainlist WHERE comment LIKE '%AndeepND |%' OR comment LIKE '%[ph5lt]'"
        )
        return True

    return False
