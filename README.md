# pihole5-list-tool
[![PyPI version](https://badge.fury.io/py/pihole5-list-tool.svg)](https://badge.fury.io/py/pihole5-list-tool)

This tool allows quickly bulk adding __block lists__ to your [Pi-hole 5](https://pi-hole.net/) setup.


Currently there are three _sources_ available to use:
- [firebog.net](https://firebog.net/)
  - Non-crossed lists: For when someone is usually around to whitelist falsely blocked sites
  - Ticked lists: For when installing Pi-hole where no one will be whitelisting falsely blocked sites
  - All lists: For those who will always be around to whitelist falsely blocked sites
-  A file you have - one url per line
-  Pasting in a list - one url per line

After adding lists, they must be loaded by running `pihole -g`, which this will offer to do for you.

You'll of course see each of them listed in the **Web Admin** interface along with a comment to help identify them

<b>NOTE:</b> If you need/want the blocklists added from [firebog.net](https://firebog.net/) (and more) continually maintained, check out [pihole-updatelists](https://github.com/jacklul/pihole-updatelists) which 
will also run great on a Pi.



## requirements
- working [pi-hole 5.0](https://pi-hole.net) installation
- [python 3.6+](https://python.org/) is required. That is available by default on at least Raspbian 10, so it should be available on your system.


## installation
If you don't **sudo pip3 install**, things won't work - possibly in a very confusing way. Definitely on Raspbian 10, so probably before that.

```bash
$ sudo pip3 install pihole5-list-tool
```

## running
Simply run:
```bash
$ sudo pihole5-list-tool
```

Here's what installing and running it will look like:

[![asciicast](https://asciinema.org/a/331296.svg)](https://asciinema.org/a/331296)