"""Utils"""
import sys
import os
import subprocess
from subprocess import CalledProcessError
import re
import json
from urllib.parse import urlparse
from json.decoder import JSONDecodeError
from colors import color
import constants


def valid_url(url):
    """make sure we have a valid url"""
    parts = urlparse(url.strip())
    return parts.scheme != "" and parts.netloc != ""


def validate_host(value):
    """ Make sure we at least have "site.com" and the TLD is long enough"""
    parts = value.split(".")
    return len(parts) > 1 and len(parts[len(parts) - 1]) > 1


def validate_regex(value):
    """ see if we have a valid regex """
    try:
        re.compile(value)
        return True
    except re.error:
        return False


def process_lines(data, comment, full_url_only=True):
    """massage the lines so we have good ones"""
    new_data = []
    extra_comment = ""
    for line in data.split("\n"):
        line = line.strip()
        if line == "":
            extra_comment = ""
            continue
        # comments!
        if line.startswith("#"):
            extra_comment += line[1:].strip() + " "
            continue

        full_comment = comment
        if extra_comment.strip() != "":
            full_comment += " - " + extra_comment

        if full_url_only:
            if valid_url(line):
                new_data.append(
                    {"url": line, "comment": full_comment, "type": constants.URL}
                )
                continue
        else:
            if validate_host(line):
                new_data.append(
                    {"url": line, "comment": full_comment, "type": constants.URL}
                )
                continue

            if validate_regex(line):
                new_data.append(
                    {"url": line, "comment": full_comment, "type": constants.REGEX}
                )
                continue

        warn(f"Skipping: {line}")

    return new_data


def find_docker():
    """ try to find a running docker image and its config """
    # return [True, '/etc/pihole/gravity.db']
    try:
        result = subprocess.run(
            ["docker", "inspect", "pihole"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except (CalledProcessError, FileNotFoundError):
        warn("docker not found running, continuing...")
        return [False, None]

    if result.returncode != 0:
        warn("docker pihole image not found running, continuing...")
        return [False, None]

    try:
        config = json.loads(result.stdout)
    except JSONDecodeError:
        return [False, None]

    if (
        not config[0]
        or not config[0]["HostConfig"]
        or not config[0]["HostConfig"]["Binds"]
    ):
        warn("unable to find config for running docker pihole image, continuing...")
        return [False, None]

    for row in config[0]["HostConfig"]["Binds"]:
        parts = row.split(":")
        if parts[1].startswith("/etc/pihole"):
            path = f"{parts[0]}/gravity.db"
            if os.path.exists(path):
                return [True, path]

    warn("unable to find config for running docker pihole image, continuing...")
    return [False, result.stdout]


def clear():
    """ helperto clear screen """
    # for windows
    if os.name == "nt":
        _ = os.system("cls")
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system("clear")


def warn(msg):
    """print styled WARNING messages"""
    print(color(msg, fg="yellow"))


def success(msg):
    """print styled SUCCESS messages"""
    print(color(msg, fg="lime"))


def info(msg):
    """print styled INFO messages"""
    print(color(msg, fg="#5DADE2"))


def danger(msg):
    """print styled DANGER messages"""
    print(color(msg, fg="orangered"))


def die(msg):
    """exit the program in style"""
    danger(msg)
    sys.exit(-1)
