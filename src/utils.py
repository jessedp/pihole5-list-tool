"""Utils"""
import sys
from urllib.parse import urlparse
from colors import color


def valid_url(url):
    """make sure we have a valid url"""
    parts = urlparse(url.strip())
    return parts.scheme and parts.netloc


def process_lines(data, comment):
    """massage the lines so we have good ones"""
    new_data = []
    for line in data.strip().split("\n"):
        line = line.strip()
        if line == '':
            continue
        if not valid_url(line):
            warn(f'Skipping: {line}')
        else:
            new_data.append({'url': line, 'comment': comment})
    return new_data


def warn(msg):
    """print styled WARNING messages"""
    print(color(msg, fg='yellow'))


def success(msg):
    """print styled SUCCESS messages"""
    print(color(msg, fg='lime'))


def info(msg):
    """print styled INFO messages"""
    print(color(msg, fg='#5DADE2'))


def die(msg):
    """exit the program in style"""
    print(color(msg, fg='orangered'))
    sys.exit(-1)
