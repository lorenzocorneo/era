import os

_countries = dict()

dataset_path = os.path.join(os.path.dirname(__file__),
                            'dataset/country_continent.csv')

with open(dataset_path) as f:
    _countries = {
        l.split(",")[0]: l.rstrip("\n").split(",")[1]
        for l in f.readlines()
    }


def get_continent(isocode):
    return _countries.get(isocode)


def get_countries(continent):
    return [
        country for country, cont in _countries.items()
        if continent.upper() == cont
    ]
