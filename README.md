# pihole5-list-tool

[![PyPI version](https://badge.fury.io/py/pihole5-list-tool.svg)](https://badge.fury.io/py/pihole5-list-tool)
[![PyPI downloads](https://img.shields.io/pypi/dm/pihole5-list-tool)](https://pypi.org/project/pihole5-list-tool/)

This tool provides bulk operations to manage your [Pi-hole 5](https://pi-hole.net/) __Allow lists__ and __Block/Ad lists__.

## Features:
  * __Allow lists__ can be [added](#allowlists) from [anudeepND's allowlist](https://github.com/anudeepND/whitelist), files, or manual entry
  * __Block/Ad lists__ can be [added](#adblocklists) from [firebog.net](https://firebog.net/), files, or manual entry
  *  __Removes__ lists it adds (or all of them)
  *  __Reset__ lists to Pi-hole defaults
  *  __Stats__ provides some quick sums and groupings
  *  __Docker__  if you're running the [pihole docker image](https://hub.docker.com/r/pihole/pihole/) (or one named `pihole`), it should be detected
and offered as a default option

## requirements

* working [pi-hole 5+](https://pi-hole.net) installation
* [python 3.6+](https://python.org/) (available by default on Raspbian 10, probably available on your system)

## installation

``` bash
$ sudo pip3 install pihole5-list-tool --upgrade
```
_Note:_
* If the `pip3` command doesn't work, try using `pip`  instead. Here are additional [options /workarounds](https://stackoverflow.com/questions/40832533/pip-or-pip3-to-install-packages-for-python-3) (and glimpses into Python peculiarities)
* You __must__ use `sudo`

## usage / running

Simply run:

``` bash
$ sudo pihole5-list-tool
```

This is what installing and running it basically looks like (many features have been added since this):

[![asciicast](https://asciinema.org/a/331296.svg)](https://asciinema.org/a/331296)


## supported sources

*TL; DR* - some maintained online lists, anything you can paste, or a file

### allowlists

Currently the only source for maintained whitelists is [anudeepND's allowlist](https://github.com/anudeepND/whitelist). They are presented as:

* __Allowlist Only__ - Domains that are safe to allow i.e does not contain any tracking or

        advertising sites. This fixes many problems like YouTube watch history,
        videos on news sites and so on.

* __Allowlist+Optional__ - These are needed depending on the service you use. They may contain some

        tracking sites but sometimes it's necessary to add bad domains to make a
        few services to work.

* __Allowlist+Referral__ - People who use services like Slickdeals and Fatwallet need a few sites

        (most of them are either trackers or ads) to be whitelisted to work
        properly. This contains some analytics and ad serving sites like
        doubleclick.net and others. If you don't know what these services are,
        stay away from this list. Domains that are safe to whitelist i.e does
        not contain any tracking or advertising sites. This fixes many problems
        like YouTube watch history, videos on news sites and so on.

### ad/blocklists

Currently the only source for maintained blocklists is [firebog.net](https://firebog.net/)

* __Non-crossed lists__: For when someone is usually around to whitelist falsely blocked sites
* __Ticked lists__: For when installing Pi-hole where no one will be whitelisting falsely blocked sites
* __All lists__: For those who will always be around to whitelist falsely blocked sites

### file/paste

Both list types allow providing either a __pasted in list__ or a __file__ as your source of lists.

### Finishing up

After adding lists, they must be loaded by running:

``` bash
$ pihole -g
```

This tool will offer to do that for you.

When that finishes, you'll see each of listed in the **Web Admin** interface along with a comment to help identify them.

**NOTE:** If you need/want the blocklists added from [firebog.net](https://firebog.net/) (and more) continually updated, check out [pihole-updatelists](https://github.com/jacklul/pihole-updatelists) which will also run great on a Pi.

