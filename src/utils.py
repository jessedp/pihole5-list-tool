"""Utils"""
import sys
from colors import color


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
