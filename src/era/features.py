import os
import json
import argparse
import itertools
import subprocess

from typing import List, Tuple, Any
from toolz.functoolz import do
from probes import get_probes_by_continent_comma_sep, get_archive
from store import get_scheduled_measurements
from domain import Measurement
from endpoints import ep_lookup
from config import results_dir

from datetime import datetime
from ripe.atlas.cousteau import AtlasResultsRequest

probes_archive = get_archive()


def _set_field(obj: Any, field: str, val: Any) -> Any:
    return do(lambda x: setattr(x[0], x[1], x[2]), (obj, field, val))[0]


def credit_balancing(measurements: List[Measurement],
                     keys: List[str]) -> List[Measurement]:
    """
    Round robin allocation between measurements and API keys
    Keyword Arguments:
    measurements: List[Measurement] --
    keys: List[str]                 --
    """
    # return [do(lambda x: setattr(x[0], "key", x[1]), (m, k))[0]
    #         for m, k in zip(measurements, itertools.cycle(keys))]
    return [
        _set_field(m, "key", k)
        for m, k in zip(measurements, itertools.cycle(keys))
    ]


# ms = [Measurement("m" + str(x)) for x in range(10)]
# ks = ["k" + str(x) for x in range(3)]
# print(credit_balancing(ms, ks))


def mesh(ips: List[str]) -> List[Tuple[str, str]]:
    """
    Keyword Arguments:
    ips: List[Measurement] --
    """
    # Sort probe ids and add them only if they have an IP address
    ids = sorted([
        int(i) for i in ips if int(i) in probes_archive
        and probes_archive[int(i)].get("address_v4")
    ])

    # Optimization to limit the number of measurements. Delivers
    # combination without repetition yet covers all the cases. Perks,
    # there is a path between every couple of ids but only one way
    # (side effect of avoiding combinations repetition). The last
    # element does not have any probes involved then it is removed.
    return [(probes_archive[m]["address_v4"],
             ",".join([str(i) for i in ids[i + 1:]]))
            for i, m in enumerate(ids)][:-1]


def set_project(measurements: List[Measurement],
                project: str) -> List[Measurement]:
    """Sets the project name and returns the list of measurements"""
    # return [do(lambda x: setattr(x[0], "project", x[1]), (m, p)) for m,
    #         p in zip(measurements, itertools.cycle([project]))]
    return [_set_field(m, "project", project) for m in measurements]


def run_measurement(m: Measurement) -> Measurement:
    out = subprocess.run(m.command().split(), capture_output=True)

    # TODO: At some point ignore --dry-run measurements
    if len(out.stdout.decode("utf-8")) and "--dry-run" not in m.command():
        m.mid = int(out.stdout.decode("utf-8"))
    else:
        print(out.stdout.decode("utf-8"))

    if len(out.stderr.decode("utf-8")) > 0:
        print(out.stderr.decode("utf-8"))

    return m


def compose_measurements(parser: argparse.ArgumentParser,
                         argv: List[str]) -> List[Measurement]:
    """
    Keyword Arguments:
    parser: argparse.ArgumentParser --
    """
    ms: List[Measurement]
    args, unknown = parser.parse_known_args(argv)

    # First arguments that can generate more than one measurements
    if args.mtype == "failed":
        return get_scheduled_measurements()

    if args.mesh:
        ms = [
            Measurement(args.mtype, x[0], probes=x[1])
            for x in mesh(args.mesh.split(","))
        ]

    if args.multi_target:
        ms = [
            Measurement(args.mtype,
                        ep_lookup(t).address if ep_lookup(t) else t)
            for t in args.multi_target
        ]

    # Then arguments that are applied to all the measurements
    if args.from_continent and args.num_probes_per_country:
        probes = get_probes_by_continent_comma_sep(args.from_continent,
                                                   args.num_probes_per_country)
        ms = [_set_field(m, "probes", probes) for m in ms]
    if args.balance and args.keys:
        ms = [
            _set_field(m, "key", k)
            for m, k in zip(ms, itertools.cycle(args.keys))
        ]
    if args.proj:
        ms = [_set_field(m, "project", args.proj) for m in ms]

    # Remaining ripe-atlas parameters
    if unknown:
        ms = [_set_field(m, "ripe_params", " ".join(unknown)) for m in ms]
    return ms


def delta_update(m: Measurement) -> Measurement:
    # Create results directory if it does not exists.
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    if not os.path.isfile(os.path.join(
            results_dir,
            str(m.mid) + ".json")) or not m.last_updated:
        # Download everything
        is_success, result = AtlasResultsRequest(**{"msm_id": m.mid}).create()

        if is_success and len(result) > 0:
            json.dump(
                result,
                open(os.path.join(results_dir,
                                  str(m.mid) + ".json"), "w"))
            m.last_updated = int(datetime.utcnow().timestamp())
    else:
        # Download and add to existing file the delta update
        is_success, result = AtlasResultsRequest(
            **{
                "msm_id": m.mid,
                "start": datetime.fromtimestamp(m.last_updated)
            }).create()
        print("Downloaded result length:", len(result))
        if is_success and len(result) > 0:
            local_result = json.load(
                open(os.path.join(results_dir,
                                  str(m.mid) + ".json"), "r"))
            print("local result length: ", str(len(local_result)))
            local_result.extend(result)
            print("Updated result length: ", str(len(local_result)))
            json.dump(
                local_result,
                open(os.path.join(results_dir,
                                  str(m.mid) + ".json"), "w"))
        if is_success:
            m.last_updated = (int(datetime.utcnow().timestamp()))
    return m
