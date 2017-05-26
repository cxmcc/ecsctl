from .cmds import cli
from .config import default_config


def main():
    cli(obj=default_config)

if __name__ == '__main__':
    main()
