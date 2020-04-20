import argparse
from typing import List
from domain import Measurement
from store import get_completed_measurements, get_scheduled_measurements


def pipeline(argv: List[str]) -> str:
    return output(parse(argv))


def parse(argv: List[str]) -> List[Measurement]:
    """
    Return a list of completed measurements from the local storage if
    the local measurements satisfy the filters (ids and project).
    """
    if len(argv) == 0:
        print("Enter either measurement ids or a project name.")
    parser = argparse.ArgumentParser()
    parser.add_argument("type",
                        choices=("completed", "failed"),
                        help="Type of measurement to be shown.")
    parser.add_argument("--proj", type=str, help="Project name")
    args = parser.parse_args(argv)

    type_map = {
        "completed": get_completed_measurements(),
        "failed": get_scheduled_measurements()
    }
    return [
        m for m in type_map[args.type]
        if not args.proj or args.proj and m.project == args.proj
    ]


def output(ms: List[Measurement]) -> str:
    """
    Process a list of measurements and returns the output.
    """
    return "\n\n".join([m.command() for m in ms])
