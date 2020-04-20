import os
import json
import argparse
import ipaddress
from typing import List
from domain import Measurement
from config import results_dir
from store import get_completed_measurements


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
    parser.add_argument("--ids", nargs="+", help="List of measurements ids.")
    parser.add_argument("--proj", type=str, help="Project name")
    args = parser.parse_args(argv)

    ids = [int(x) for x in args.ids] if args.ids else []
    return [
        m for m in get_completed_measurements()
        if (args.ids and m.mid in ids) or (
            args.proj and m.project == args.proj)
    ]


def _extract_path(json_result: dict) -> List[str]:
    path = [json_result["from"]] + [
        x["result"][0]["from"] for x in json_result["result"]
        if "x" not in x["result"][0] and "error" not in x["result"][0]
        and not ipaddress.ip_address(x["result"][0]["from"]).is_private
    ]

    return path if path[-1] == json_result["dst_addr"] else path + [
        json_result["dst_addr"]
    ]


def _process_traceroute(m: Measurement) -> str:
    if os.path.isfile(os.path.join(results_dir, f"{m.mid}.json")):
        json_result = json.load(
            open(os.path.join(results_dir, f"{m.mid}.json"), "r"))
        paths = [_extract_path(m) for m in json_result]
        return "\n".join([",".join(p) for p in paths])
    return ""


def _process_ping(m: Measurement) -> str:
    if os.path.isfile(os.path.join(results_dir, f"{m.mid}.json")):
        json_result = json.load(
            open(os.path.join(results_dir, f"{m.mid}.json"), "r"))
        rtts = [
            str(x["prb_id"]) + "," + x["dst_addr"] + "," + str(rtt["rtt"])
            for x in json_result for rtt in x["result"]
        ]
        return "\n".join(rtts)
    return ""


def output(ms: List[Measurement]) -> str:
    """
    Process a list of measurements and returns the output.
    """
    if len(ms) > 0 and ms[0].mtype == "traceroute":
        return "\n".join([_process_traceroute(m) for m in ms])
    return "\n".join([_process_ping(m) for m in ms])
