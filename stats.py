""" variaous stats and stat displays """

from terminaltables import AsciiTable, SingleTable
from colors import color
import utils

stats = {
    "total_adlist": "SELECT COUNT(*) FROM adlist",
    "total_adlist_enabled": "SELECT COUNT(*) FROM adlist WHERE enabled = 1",
    "total_adlist_disabled": "SELECT COUNT(*) FROM adlist WHERE enabled = 0",
    "our_adlist": "SELECT COUNT(*) FROM adlist WHERE comment LIKE '%Firebog |%' OR comment LIKE '%[ph5lt]'",
    "our_adlist_enabled": "SELECT COUNT(*) FROM adlist WHERE enabled = 1 AND (comment LIKE '%Firebog |%' OR comment LIKE '%[ph5lt]')",
    "our_adlist_disabled": "SELECT COUNT(*) FROM adlist WHERE enabled = 0 AND (comment LIKE '%Firebog |%' OR comment LIKE '%[ph5lt]')",
    "other_adlist": "SELECT COUNT(*) FROM adlist WHERE comment NOT LIKE '%Firebog |%' AND comment NOT LIKE '%[ph5lt]'",
    "other_adlist_enabled": "SELECT COUNT(*) FROM adlist WHERE enabled = 1 AND comment NOT LIKE '%Firebog |%' AND comment NOT LIKE '%[ph5lt]'",
    "other_adlist_disabled": "SELECT COUNT(*) FROM adlist WHERE enabled = 0 AND comment NOT LIKE '%Firebog |%' AND comment NOT LIKE '%[ph5lt]'",
    "total_allow": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2)",
    "total_allow_enabled": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND enabled = 1",
    "total_allow_disabled": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND enabled = 0",
    "our_allow": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND comment LIKE '%AndeepND |%' OR comment LIKE '%[ph5lt]'",
    "our_allow_enabled": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND enabled = 1 AND (comment LIKE '%AndeepND |%' OR comment LIKE '%[ph5lt]')",
    "our_allow_disabled": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND enabled = 0 AND (comment LIKE '%AndeepND |%' OR comment LIKE '%[ph5lt]')",
    "other_allow": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND comment NOT LIKE '%AndeepND |%' AND comment NOT LIKE '%[ph5lt]'",
    "other_allow_enabled": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND enabled = 1 AND comment NOT LIKE '%AndeepND |%' AND comment NOT LIKE '%[ph5lt]'",
    "other_allow_disabled": "SELECT COUNT(*) FROM domainlist WHERE type IN (0,2) AND enabled = 0 AND comment NOT LIKE '%AndeepND |%' AND comment NOT LIKE '%[ph5lt]'",
}


def get(cur, name):
    """ get stats using prebuilt statements """
    if name not in stats:
        return -1
    cur.execute(stats[name])
    return str(cur.fetchone()[0])


def adlist_top3_by_comment(cur):
    """ top 3 adlists by comment """
    sql = "SELECT comment, count(*) FROM adlist GROUP BY comment LIMIT 3"
    cur.execute(sql)
    return cur.fetchall()


def allow_top3_by_comment(cur):
    """ top 3 allow lists by comment """
    sql = "SELECT comment, count(*) FROM domainlist WHERE type IN (0,2) GROUP BY comment LIMIT 3"
    cur.execute(sql)
    return cur.fetchall()


def stat_bar(cur):
    """ one-liner stat bar """
    # Block : All=X  Ours=Y Oth=Z   |  Allow : All=X Ours=Y Oth=Z
    data = []

    data.append("Blocks Enabled:  All=" + str(get(cur, "total_adlist_enabled")))
    data.append("│")
    data.append("Ours=" + str(get(cur, "our_adlist_enabled")))
    # data.append("│")
    # data.append("Other=" + str(get(cur, "other_adlist_enabled")))

    data.append("│")
    data.append("Allows Enabled:  All=" + str(get(cur, "total_allow_enabled")))
    data.append("│")
    data.append("Ours=" + str(get(cur, "our_allow_enabled")))
    # data.append("│")
    # data.append("Other=" + str(get(cur, "other_allow_enabled")))

    table = SingleTable([data])

    table.inner_heading_row_border = False
    table.outer_border = False
    table.inner_row_border = False
    table.inner_column_border = False
    table.padding_left = 2

    print()
    print(color(table.table, bg="#505050", fg="white"))
    print()


def header(cur):
    """ a stats overview header """
    print()
    block_header(cur)
    # utils.info("──────────────────────────────────────────────────────────────")
    print()
    allow_header(cur)
    print()


def allow_header(cur):
    """ allow portion of header """

    block_data = [
        [
            "Total     :",
            get(cur, "total_allow_enabled") + "/" + get(cur, "total_allow"),
        ],
        ["Our Lists :", get(cur, "our_allow_enabled") + "/" + get(cur, "our_allow")],
        [
            "Others    :",
            get(cur, "other_allow_enabled") + "/" + get(cur, "other_allow"),
        ],
    ]
    block_table = AsciiTable(block_data)

    block_table.inner_heading_row_border = False
    block_table.outer_border = False
    block_table.inner_row_border = False
    block_table.inner_column_border = False

    rows = allow_top3_by_comment(cur)
    t3_block_data = []
    for row in rows:
        t3_block_data.append([row[0], row[1]])

    t3_block_table = AsciiTable(t3_block_data)

    t3_block_table.inner_heading_row_border = False
    t3_block_table.outer_border = False
    t3_block_table.inner_row_border = False
    t3_block_table.inner_column_border = False

    table_data = [
        ["Allowlist Stats", "Top 3 by Comment"],
        [block_table.table, t3_block_table.table],
    ]

    table = SingleTable(table_data)
    table.padding_left = 2
    table.outer_border = False

    utils.info(table.table)


def block_header(cur):
    """ block portion of header """

    block_data = [
        [
            "Total     :",
            get(cur, "total_adlist_enabled") + "/" + get(cur, "total_adlist"),
        ],
        ["Our Lists :", get(cur, "our_adlist_enabled") + "/" + get(cur, "our_adlist")],
        [
            "Others    :",
            get(cur, "other_adlist_enabled") + "/" + get(cur, "other_adlist"),
        ],
    ]
    block_table = AsciiTable(block_data)

    block_table.inner_heading_row_border = False
    block_table.outer_border = False
    block_table.inner_row_border = False
    block_table.inner_column_border = False

    rows = adlist_top3_by_comment(cur)
    t3_block_data = []
    for row in rows:
        t3_block_data.append([row[0], row[1]])

    t3_block_table = AsciiTable(t3_block_data)

    t3_block_table.inner_heading_row_border = False
    t3_block_table.outer_border = False
    t3_block_table.inner_row_border = False
    t3_block_table.inner_column_border = False

    table_data = [
        ["Ad/Blocklist Stats", "Top 3 by Comment"],
        [block_table.table, t3_block_table.table],
        [],
    ]

    table = SingleTable(table_data)
    table.padding_left = 2
    table.outer_border = False

    utils.info(table.table)
