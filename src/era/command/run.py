import socket
import argparse
from typing import List
from toolz.functoolz import compose, do, partial
from domain import Measurement
from endpoints import ENDPOINTS
from store import get_completed_measurements, update_queues
from features import compose_measurements, run_measurement


def _validate_endpoints(xs: str) -> List[bool]:
    eps = [x.uname for x in ENDPOINTS]
    ys = [x.rstrip().lstrip() for x in xs.split(",")]

    return [y in eps for y in ys]


def _validate_ips(xs: str) -> List[bool]:
    def val(x: str) -> bool:
        try:
            socket.inet_aton(x)
            return True
        except:
            return False

    return [val(x.rstrip().lstrip()) for x in xs.split(",")]


def _validate_multi_target(xs: str):
    message = 'One or more element of "{}" does not appear to'.format(xs) +\
        ' be an IP address or host or cloud endpoint(s) name'
    if not len([x for x in _validate_endpoints(xs) if x]) + len(
            [x for x in _validate_ips(xs) if x]) == len(xs.split(",")):
        raise argparse.ArgumentTypeError(message)

    return xs.split(",")


def pipeline(argv: List[str]) -> str:
    return output(parse(argv))


def parse(argv: List[str]) -> List[Measurement]:
    """
    Runs new or failed measurements.

    Keyword Arguments:
    args: List[str] --
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--multi-target", type=_validate_multi_target)
    parser.add_argument("--mesh",
                        help="Measure all to all to provided probe ids")
    parser.add_argument(
        "mtype",
        choices=("ping", "traceroute", "failed"),
        help="Measurement type, includes also failed measurements")
    parser.add_argument("--from-continent", help="(EU|NA|SA|AS|AF|OC)")
    parser.add_argument("--num-probes-per-country", type=int)
    parser.add_argument("--run-scheduled",
                        action="store_true",
                        help="Run scheduled measurements")
    parser.add_argument("--proj",
                        type=str,
                        help="Project name, mapped to ripe description")
    parser.add_argument("--keys",
                        nargs="+",
                        help="API keys to use during balance")
    parser.add_argument("--balance", action="store_true")

    if len(argv) == 0:
        print("Enter either measurement ids or a project name.")

    return compose_measurements(parser, argv)


def _run_measurement(m: Measurement) -> Measurement:
    return run_measurement(m)


def output(ms: List[Measurement]) -> str:
    """
    Process a list of measurements and returns the output.
    """
    ms = do(update_queues, [_run_measurement(m) for m in ms])
    return "\n".join([
        str(m.mid) if m.mid else "FAILED" + " - " + m.description() for m in ms
    ])
