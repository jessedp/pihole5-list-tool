"""Utils"""
import sys
import os
import re
from urllib.parse import urlparse
from colors import color
import constants


def valid_url(url):
    """make sure we have a valid url"""
    parts = urlparse(url.strip())
    print(parts)
    return parts.scheme and parts.netloc


def validate_host(value):
    """ Make sure we at least have "site.com" and the TLD is long enough"""
    parts = value.split('.')
    return len(parts) > 1 and len(parts[len(parts)-1]) > 1


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
    extra_comment = ''
    for line in data.strip().split("\n"):
        line = line.strip()
        if line == '':
            extra_comment = ''
            continue
        # comments!
        if line.startswith('#'):
            extra_comment += line[1:].strip() + ' '
            continue

        full_comment = comment
        if extra_comment.strip() != '':
            full_comment += ' - ' + extra_comment

        if full_url_only:
            if valid_url(line):
                new_data.append({'url': line, 'comment': full_comment, 'type': constants.URL})
                continue
        else:
            if validate_host(line):
                new_data.append({'url': line, 'comment': full_comment, 'type': constants.URL})
                continue

            if validate_regex(line):
                new_data.append({'url': line, 'comment': full_comment, 'type': constants.REGEX})
                continue

        warn(f'Skipping: {line}')

    return new_data


def clear():
    """ helperto clear screen """
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')


def warn(msg):
    """print styled WARNING messages"""
    print(color(msg, fg='yellow'))


def success(msg):
    """print styled SUCCESS messages"""
    print(color(msg, fg='lime'))


def info(msg):
    """print styled INFO messages"""
    print(color(msg, fg='#5DADE2'))


def danger(msg):
    """print styled DANGER messages"""
    print(color(msg, fg='orangered'))


def die(msg):
    """exit the program in style"""
    danger(msg)
    sys.exit(-1)
