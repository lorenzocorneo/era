import sys
import argparse

import command.run as run
import command.show as show
import command.update as update
import command.process as process


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        choices=("run", "update", "process", "show"),
                        help='Subcommand to run')
    args = parser.parse_args(sys.argv[1:2])
    output = getattr(sys.modules["command." + args.command],
                     "pipeline")(sys.argv[2:])
    print(output)


if __name__ == '__main__':
    main()
