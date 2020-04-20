import json
import subprocess
from typing import List
from continents import get_countries
from config import probes_archive

# TODO: Add random selection of `amount` probes in the continent


# Get `amount` probes per every country in the continent.
def get_probes_by_continent(continent: str, amount: int) -> List[int]:
    countries = get_countries(continent)
    out = [
        subprocess.run(
            "ripe-atlas probe-search --country {} --ids-only --status 1 --limit {}"
            .format(c, amount).split(),
            capture_output=True) for c in countries
    ]

    return [
        int(y) for x in out for y in x.stdout.decode("utf-8").split("\n")
        if len(y) > 0
    ]


def get_probes_by_continent_comma_sep(continent: str, amount: int) -> str:
    return ",".join(
        [str(x) for x in get_probes_by_continent(continent, amount)])


def get_archive() -> dict:
    return {x["id"]: x for x in json.load(open(probes_archive, "r"))["objects"]}
