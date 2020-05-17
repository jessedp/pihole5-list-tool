# pihole5-list-tool
This tool allows quickly bulk adding __block lists__ to your [Pi-hole 5](https://pi-hole.net/) setup.


Currently there are three _sources_ available to use:
- [firebog.net](https://firebog.net/)
  - Non-crossed lists: For when someone is usually around to whitelist falsely blocked sites
  - Ticked lists: For when installing Pi-hole where no one will be whitelisting falsely blocked sites
  - All lists: For those who will always be around to whitelist falsely blocked sites
-  A file you have
-  Pasting in a list


The source of each list is visible in the web interface and an option to load the lists for immediate use is available after adding.

## installation
This requires [python 3.6+](https://python.org/).

```bash
$ sudo pip install pihole5-list-tool
```

## running
Running the tool should go something like this:
