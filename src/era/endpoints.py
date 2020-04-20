import os
import csv
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CloudEndpoint:
    uname: str
    address: str
    continent: str
    country: str
    countrycode: str
    city: str
    provider: str
    longitude: float
    latitude: float


ENDPOINTS: List[CloudEndpoint]
_ENDPOINTS_DICT: Dict[str, CloudEndpoint]

dataset_path = os.path.join(os.path.dirname(__file__), 'dataset/endpoints.csv')

with open(dataset_path) as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    ENDPOINTS = [
        CloudEndpoint(l[0], l[1], l[2], l[3], l[4], l[5], l[6], float(l[7]),
                      float(l[8])) for l in reader
    ]

_ENDPOINTS_DICT = {c.uname: c for c in ENDPOINTS}


# TODO: use Maybe monad as return type
def ep_lookup(x: str):
    return _ENDPOINTS_DICT.get(x)
