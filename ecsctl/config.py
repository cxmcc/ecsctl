
import os
import click
from configparser import RawConfigParser


__all__ = ['read_config', 'update_config', 'default_config']

APP_NAME = SECTION = 'ecsctl'
APP_DIR = click.get_app_dir(APP_NAME)
CONFIG_FILE = os.path.join(APP_DIR, 'config')

default_config = {
    'cluster': 'default',
    'docker_port': 2375,
}

def get_config_parser():
    parser = RawConfigParser()
    parser.read([CONFIG_FILE])
    return parser


def read_config():
    parser = get_config_parser()
    rv = {}
    for section in parser.sections():
        if section != SECTION:
            continue
        for key, value in parser.items(section):
            rv[key] = value
    return rv

def update_config(key, value):
    parser = get_config_parser()
    if not parser.has_section(SECTION):
        parser.add_section(SECTION)
    parser.set(SECTION, key, value)
    if not os.path.exists(APP_DIR):
        os.mkdir(APP_DIR)
    with open(CONFIG_FILE, 'w') as f:
        parser.write(f)
