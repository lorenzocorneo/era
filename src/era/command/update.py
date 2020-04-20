import argparse
from typing import List
from toolz.functoolz import compose, do, partial
from domain import Measurement
from store import get_completed_measurements, update_queues
from features import delta_update


def pipeline(argv: List[str]) -> str:
    return output(parse(argv))


# todo: redundant code. make it reusable in another module
def parse(argv: List[str]) -> List[Measurement]:
    """
    Updates measurements results: individual, multiple measurements
    ids or project
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids",
                        nargs="+",
                        help="Comma separated list of measurements ids.")
    parser.add_argument("--proj", type=str, help="Project name")
    args = parser.parse_args(argv)

    if len(argv) == 0:
        print("Enter either measurement ids or a project name.")

    ids = [int(x) for x in args.ids] if args.ids else []
    return [
        m for m in get_completed_measurements()
        if (args.ids and m.mid in ids) or (
            args.proj and m.project == args.proj)
    ]


def _update_measurement(m: Measurement) -> Measurement:
    return delta_update(m)


def output(ms: List[Measurement]) -> str:
    """
    Process a list of measurements and returns the output.
    """
    ret = do(update_queues, [_update_measurement(m) for m in ms])
    return "\n".join([str(m) for m in ret])
